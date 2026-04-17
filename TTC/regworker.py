"""
TTCRegWorker - Multi-threading worker cho TTC account registration
Chạy registration tài khoản TTC trong thread riêng
"""

from PyQt5.QtCore import QThread, pyqtSignal


class TTCRegWorker(QThread):
    """Tạo 1 TTC account trong thread riêng."""
    done = pyqtSignal(str, dict)  # worker_id, result_dict
    log_msg = pyqtSignal(str)     # log message
    
    def __init__(self, worker_id: str, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id

    def run(self):
        from TTC.REG import RegTDS
        
        try:
            self.log_msg.emit(f"[→] Worker {self.worker_id}: Bắt đầu tạo TTC account...")
            reg = RegTDS()
            result = reg.run()
            
            if result:
                self.log_msg.emit(f"[✔] Worker {self.worker_id}: Tạo OK - {result.get('username')}")
                self.done.emit(self.worker_id, {
                    "ok": True,
                    "username": result.get("username"),
                    "password": result.get("password"),
                    "token": result.get("tokentds", ""),
                })
            else:
                self.log_msg.emit(f"[✘] Worker {self.worker_id}: Tạo thất bại")
                self.done.emit(self.worker_id, {"ok": False, "msg": "Đăng ký thất bại"})
        
        except Exception as e:
            self.log_msg.emit(f"[✘] Worker {self.worker_id}: Exception - {str(e)}")
            self.done.emit(self.worker_id, {"ok": False, "msg": str(e)})


class TTCRegBatchManager:
    """Quản lý pool thread để tạo nhiều TTC account cùng lúc."""
    
    def __init__(self, num_accounts: int, max_threads: int = 3, callbacks=None):
        """
        num_accounts: Số tài khoản cần tạo
        max_threads: Số luồng tối đa chạy đồng thời
        callbacks: dict with keys: log_msg, one_done, all_done
        """
        self._total = num_accounts
        self._max = max_threads
        self._active = {}
        self._created_count = 0
        self._results = []
        self._callbacks = callbacks or {}

    def start(self):
        """Bắt đầu tạo accounts."""
        for i in range(min(self._total, self._max)):
            self._spawn_worker(i)

    def _spawn_worker(self, index: int):
        """Tạo và khởi động 1 worker."""
        worker_id = f"Worker-{index + 1}"
        w = TTCRegWorker(worker_id)
        w.done.connect(self._on_done)
        
        if "log_msg" in self._callbacks:
            w.log_msg.connect(self._callbacks["log_msg"])
        
        self._active[worker_id] = w
        w.start()

    def _on_done(self, worker_id, result):
        """Khi 1 worker hoàn thành."""
        w = self._active.pop(worker_id, None)
        if w:
            w.quit()
            w.wait()
        
        # Lưu kết quả
        if result.get("ok"):
            self._results.append(result)
        
        self._created_count += 1
        
        # Gọi callback one_done
        if "one_done" in self._callbacks:
            self._callbacks["one_done"](worker_id, result)
        
        # Tạo worker tiếp nếu còn
        if self._created_count < self._total:
            next_index = self._created_count
            self._spawn_worker(next_index)
        
        # Kiểm tra xem có hoàn thành tất cả không
        if not self._active and self._created_count >= self._total:
            if "all_done" in self._callbacks:
                self._callbacks["all_done"](self._results)

    def cleanup(self):
        """Dừng tất cả threads."""
        for w in list(self._active.values()):
            w.quit()
            w.wait()
        self._active.clear()


class CheckXuWorker(QThread):
    """Kiểm tra XU cho 1 tài khoản TTC trong thread riêng."""
    progress_update = pyqtSignal(str, int, int)  # username, current, total
    done = pyqtSignal(str, int)  # username, xu
    
    def __init__(self, username: str, api_key: str, total: int, index: int, parent=None):
        super().__init__(parent)
        self.username = username
        self.api_key = api_key
        self.total = total
        self.index = index

    def run(self):
        try:
            self.progress_update.emit(self.username, self.index, self.total)
            from TTC.REG import Checkxu
            checker = Checkxu(self.api_key)
            xu = checker.checkxu()
            if xu is not None:
                self.done.emit(self.username, xu)
        except Exception:
            pass


class CheckXuBatchManager:
    """Quản lý pool thread để kiểm tra XU nhiều tài khoản cùng lúc."""
    
    def __init__(self, users: list, max_threads: int = 5, callbacks=None):
        """
        users: List[{username, api_key}]
        max_threads: Số luồng tối đa chạy đồng thời
        callbacks: dict with keys: progress, one_done, all_done
        """
        self._users = users
        self._total = len(users)
        self._max = max_threads
        self._active = {}
        self._checked_count = 0
        self._results = {}
        self._callbacks = callbacks or {}

    def start(self):
        """Bắt đầu kiểm tra XU."""
        for i in range(min(self._total, self._max)):
            self._spawn_worker(i)

    def _spawn_worker(self, index: int):
        """Tạo và khởi động 1 worker."""
        if index >= self._total:
            return
        
        user_info = self._users[index]
        w = CheckXuWorker(user_info["username"], user_info["api_key"], self._total, index + 1)
        w.progress_update.connect(self._on_progress)
        w.done.connect(self._on_done)
        
        self._active[user_info["username"]] = w
        w.start()

    def _on_progress(self, username, current, total):
        """Cập nhật tiến độ."""
        if "progress" in self._callbacks:
            self._callbacks["progress"](username, current, total)

    def _on_done(self, username, xu):
        """Khi 1 worker hoàn thành."""
        w = self._active.pop(username, None)
        if w:
            w.quit()
            w.wait()
        
        self._results[username] = xu
        self._checked_count += 1
        
        # Gọi callback one_done
        if "one_done" in self._callbacks:
            self._callbacks["one_done"](username, xu)
        
        # Tạo worker tiếp nếu còn
        if self._checked_count < self._total:
            self._spawn_worker(self._checked_count)
        
        # Kiểm tra xem có hoàn thành tất cả không
        if not self._active and self._checked_count >= self._total:
            if "all_done" in self._callbacks:
                self._callbacks["all_done"](self._results)

    def cleanup(self):
        """Dừng tất cả threads."""
        for w in list(self._active.values()):
            w.quit()
            w.wait()
        self._active.clear()
