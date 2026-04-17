"""
RegPageWorker - Async worker threads for page registration + avatar/cover setup
Handles: REG page, upload avatar, set avatar, upload cover, set cover
"""

import os
import random
import requests
import shutil
from PyQt5.QtCore import QThread, pyqtSignal


class RegisterWorker(QThread):
    """Chạy registration cho 1 page trong thread riêng (REG + Avatar + Cover)."""
    done    = pyqtSignal(str, dict)   # page_id, result_dict
    log_msg = pyqtSignal(str)         # log message
    status_update = pyqtSignal(str, str)  # page_id, status

    def __init__(self, page_id: str, reg_data: dict, settings: dict = None, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.reg_data = reg_data
        self.settings = settings or {}
        print(self.settings)

    def run(self):
        from source.REGPRO5 import REGPRO5
        
        cookie = self.reg_data.get("cookie", "")
        # bio = self.reg_data.get("bio", "")
        # name = self.reg_data.get("name", "")
        page_uid = self.reg_data.get("page_uid", "")  # UID tài khoản chủ sở hữu
        acc_token = self.reg_data.get("token", "")    # User token để lấy page token
        
        name = random.choice(self.settings.get("names", "Page").split("|"))
        bio = random.choice(self.settings.get("bios", "Chào mừng bạn").split("|"))

        # STEP 1: Register page
        self.status_update.emit(self.page_id, "⏳ Đang REG...")
        self.log_msg.emit(f"[→] Đang tạo page: {name}")
        
        try:
            reg = REGPRO5(cookie)
            if not reg.login():
                self.status_update.emit(self.page_id, "✘ Login fail")
                self.log_msg.emit(f"[✘] Login lỗi: {name}")
                self.done.emit(self.page_id, {"ok": False, "msg": "Cookie không hợp lệ"})
                return
            
            result = reg.REG(bio, name)
            
            # Handle result from REGPRO5.REG() - now returns dict
            if not result.get("ok"):
                self.status_update.emit(self.page_id, "✘ REG fail")
                error_msg = result.get("error", "Lỗi không xác định")
                self.log_msg.emit(f"[✘] REG FAIL: {name} — {error_msg}")
                self.done.emit(self.page_id, {"ok": False, "msg": error_msg})
                return
            
            created_page_id = result.get("page_id", "")
            if not created_page_id:
                self.status_update.emit(self.page_id, "✘ REG fail")
                self.log_msg.emit(f"[✘] REG FAIL: {name} — No page ID returned")
                self.done.emit(self.page_id, {"ok": False, "msg": "No page ID returned"})
                return
            
            self.log_msg.emit(f"[✔] REG OK: {name} (ID: {created_page_id})")
            self.status_update.emit(self.page_id, "✔ REG OK")
            
            # STEP 2: Setup Avatar + Cover (if configured and we have token)
            avatar_set = False
            cover_set = False
            
            if acc_token and created_page_id:
                try:
                    # Lấy Page Token từ User Token
                    url = "https://graph.facebook.com/v19.0/me/accounts"
                    params = {"access_token": acc_token}
                    res = requests.get(url, params=params, timeout=10)
                    pages_list = res.json().get("data", [])
                    
                    page_token = None
                    for p in pages_list:
                        if p["id"] == created_page_id:
                            page_token = p.get("access_token")
                            break
                    
                    if page_token:
                        # Setup Avatar nếu có
                        avatar_path = self.settings.get("avatar_path")
                        if avatar_path:
                            avatar_file = self._get_image_from_path(avatar_path)
                            if avatar_file:
                                avatar_set = self._set_avatar(created_page_id, page_token, avatar_file)
                                if avatar_set:
                                    # Lưu avatar vào folder image/
                                    self._save_avatar_local(avatar_file, created_page_id)
                                    self.log_msg.emit(f"[✔] Avatar set + saved: {name}")
                        
                        # Setup Cover nếu có
                        cover_path = self.settings.get("cover_path")
                        if cover_path:
                            cover_file = self._get_image_from_path(cover_path)
                            if cover_file:
                                cover_set = self._set_cover(created_page_id, page_token, cover_file)
                                if cover_set:
                                    self.log_msg.emit(f"[✔] Cover set: {name}")
                    else:
                        self.log_msg.emit(f"[⚠] Không tìm được page token, bỏ qua avatar/cover: {name}")
                
                except Exception as e:
                    self.log_msg.emit(f"[⚠] Lỗi setting avatar/cover: {name} — {e}")
            
            self.status_update.emit(self.page_id, "✔ Done")
            self.done.emit(self.page_id, {
                "ok": True,
                "page_id": created_page_id,
                "name": name,
                "avatar_set": avatar_set,
                "cover_set": cover_set,
                "token": "",
                "cookie": ""
            })
        
        except Exception as e:
            self.status_update.emit(self.page_id, "✘ Error")
            self.log_msg.emit(f"[✘] Exception: {name} — {e}")
            self.done.emit(self.page_id, {"ok": False, "msg": str(e)})
    
    def _get_image_from_path(self, path: str) -> str:
        """
        Lấy image file từ path.
        - Nếu path là file, trả về file đó
        - Nếu path là folder, trả về random image từ folder
        - Nếu không tìm, trả về None
        """
        if not os.path.exists(path):
            return None
        
        # Nếu là file, trả về
        if os.path.isfile(path):
            return path
        
        # Nếu là folder, tìm image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        image_files = []
        
        if os.path.isdir(path):
            try:
                for file in os.listdir(path):
                    if file.lower().endswith(image_extensions):
                        full_path = os.path.join(path, file)
                        if os.path.isfile(full_path):
                            image_files.append(full_path)
                
                if image_files:
                    return random.choice(image_files)
            except Exception as e:
                self.log_msg.emit(f"[⚠] Lỗi đọc folder image: {path} — {e}")
        
        return None
    
    def _set_avatar(self, page_id: str, page_token: str, image_path: str) -> bool:
        """Upload ảnh và set làm avatar."""
        try:
            # Bước 1: Upload ảnh
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            
            with open(image_path, "rb") as f:
                files = {"source": f}
                data = {"published": "false", "access_token": page_token}
                res = requests.post(url, files=files, data=data, timeout=15)
            
            photo_result = res.json()
            if "id" not in photo_result:
                return False
            
            photo_id = photo_result["id"]
            
            # Bước 2: Set làm avatar
            url = f"https://graph.facebook.com/v19.0/{page_id}/picture"
            data = {"photo": photo_id, "access_token": page_token}
            res = requests.post(url, data=data, timeout=10)
            
            return res.status_code == 200
        except Exception as e:
            self.log_msg.emit(f"[⚠] Avatar set error: {e}")
            return False
    
    def _set_cover(self, page_id: str, page_token: str, image_path: str) -> bool:
        """Upload ảnh và set làm cover."""
        try:
            # Bước 1: Upload ảnh
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            
            with open(image_path, "rb") as f:
                files = {"source": f}
                data = {"published": "false", "access_token": page_token}
                res = requests.post(url, files=files, data=data, timeout=15)
            
            photo_result = res.json()
            if "id" not in photo_result:
                return False
            
            photo_id = photo_result["id"]
            
            # Bước 2: Set làm cover
            url = f"https://graph.facebook.com/v19.0/{page_id}"
            data = {"cover": photo_id, "access_token": page_token}
            res = requests.post(url, data=data, timeout=10)
            
            return res.status_code == 200
        except Exception as e:
            self.log_msg.emit(f"[⚠] Cover set error: {e}")
            return False
    
    def _save_avatar_local(self, source_path: str, page_id: str):
        """Lưu avatar vào folder image/ với tên avatar_{page_id}.ext"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "..", "image")
            os.makedirs(cache_dir, exist_ok=True)
            
            ext = os.path.splitext(source_path)[1] or ".jpg"
            dest_path = os.path.join(cache_dir, f"avatar_{page_id}{ext}")
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            self.log_msg.emit(f"[⚠] Lỗi lưu avatar: {e}")


class RegisterBatchManager:
    """Quản lý pool thread để register nhiều page cùng lúc."""
    def __init__(self, reg_list: list, settings: dict = None, max_threads: int = 3, callbacks=None):
        """
        callbacks: dict with keys: log_msg, one_done, all_done, status_update
                   each is a callable(msg/page_id/result/status)
        """
        self._queue = list(reg_list)
        self._max = max_threads
        self._active = {}
        self._done_count = 0
        self._total = len(reg_list)
        self._settings = settings or {}
        self._callbacks = callbacks or {}

    def start(self):
        self._fill()

    def _fill(self):
        while self._queue and len(self._active) < self._max:
            page_id, reg_data = self._queue.pop(0)
            w = RegisterWorker(page_id, reg_data, self._settings)
            w.done.connect(self._on_done)
            
            if "log_msg" in self._callbacks:
                w.log_msg.connect(self._callbacks["log_msg"])
            if "status_update" in self._callbacks:
                w.status_update.connect(self._callbacks["status_update"])
            
            self._active[page_id] = w
            w.start()

    def _on_done(self, page_id, result):
        w = self._active.pop(page_id, None)
        if w:
            w.quit()
            w.wait()
        
        self._done_count += 1
        if "one_done" in self._callbacks:
            self._callbacks["one_done"](page_id, result)
        
        self._fill()
        if not self._active and not self._queue:
            if "all_done" in self._callbacks:
                self._callbacks["all_done"]()
    
    def cleanup(self):
        """Properly stop all active threads before destruction."""
        for w in list(self._active.values()):
            w.quit()
            w.wait()
        self._active.clear()
        self._queue.clear()
