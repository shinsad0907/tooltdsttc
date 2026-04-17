import requests
import json
import time
import random
import re
from typing import Dict, Any, Optional

class CookieHandler:
    @staticmethod
    def to_dict(cookie_str: str) -> Dict[str, str]:
        return {k.strip(): v.strip() for item in cookie_str.split(";") 
                if "=" in item for k, v in [item.split("=", 1)]}

class NumberEncoder:
    @staticmethod
    def to_base36(num: int) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return "0"
        result = ""
        while num:
            num, remainder = divmod(num, 36)
            result = chars[remainder] + result
        return result

class HTMLExtractor:
    @staticmethod
    def find_pattern(html: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, html)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_token(html: str) -> Optional[str]:
        patterns = [
            r'DTSGInitialData".*?"token":"([^"]+)"',
            r'"token":"([^"]+)"',
        ]
        for pattern in patterns:
            result = HTMLExtractor.find_pattern(html, pattern)
            if result:
                return result
        return None
    
    @staticmethod
    def extract_lsd(html: str) -> Optional[str]:
        patterns = [
            r'LSD".*?"token":"([^"]+)"',
            r'"token":"([^"]+)"',
        ]
        for pattern in patterns:
            result = HTMLExtractor.find_pattern(html, pattern)
            if result:
                return result
        return None
    
    @staticmethod
    def extract_user_id(html: str) -> Optional[str]:
        patterns = [
            r'"actorID":"(\d+)"',
            r'"USER_ID":"(\d+)"',
            r'c_user=(\d+)',
        ]
        for pattern in patterns:
            result = HTMLExtractor.find_pattern(html, pattern)
            if result:
                return result
        return None
    
    @staticmethod
    def extract_revision(html: str) -> Optional[str]:
        pattern = r'client_revision["\s:]+(\d+)'
        return HTMLExtractor.find_pattern(html, pattern)
    
    @staticmethod
    def extract_jazoest(html: str) -> Optional[str]:
        pattern = r'jazoest=(\d+)'
        return HTMLExtractor.find_pattern(html, pattern)

class FacebookSession:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.token = None
        self.user_id = None
        self.revision = None
        self.jazoest = None
        self.lsd = None
    
    def authenticate(self) -> bool:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "cookie": self.cookie,
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(
                "https://www.facebook.com/",
                headers=headers,
                cookies=CookieHandler.to_dict(self.cookie),
                timeout=30
            )
            
            html = response.text
            self.token = HTMLExtractor.extract_token(html)
            self.user_id = HTMLExtractor.extract_user_id(html)
            self.revision = HTMLExtractor.extract_revision(html) or "1000000"
            self.jazoest = HTMLExtractor.extract_jazoest(html) or "0"
            self.lsd = HTMLExtractor.extract_lsd(html) or "0"
            return {
                "token": self.token or "N/A",
                "user_id": self.user_id or "N/A",
                "revision": self.revision or "N/A",
                "jazoest": self.jazoest or "N/A",
                "lsd": self.lsd or "N/A",
            }
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

class GenData:
    def __init__(self, session: FacebookSession):
        self.session = session
        self.request_counter = 0
    
    def build(self, bio: str, name: str) -> Dict[str, Any]:
        self.request_counter += 1   
        category_id = [169421023103905, 2347428775505624, 2347428775505624, 2347428775505624, 
                       192614304101075, 145118935550090, 1350536325044173, 471120789926333, 
                       180410821995109, 145118935550090, 357645644269220, 2705]
        category = random.choice(category_id) 
        payload = {
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'AdditionalProfilePlusCreationMutation',
            'server_timestamps': 'true',
            "fb_dtsg": self.session.token,
            "jazoest": self.session.jazoest,
            "__a": "1",
            "__user": self.session.user_id,
            "__req": NumberEncoder.to_base36(self.request_counter),
            "__rev": self.session.revision,
            "av": self.session.user_id,
            "lsd": self.session.lsd,
            'variables': '{"input":{"bio":"'+bio+'","categories":["'+str(category)+'"],"creation_source":"comet","name":"'+name+'","off_platform_creator_reachout_id":null,"page_referrer":"launch_point","actor_id":"'+self.session.user_id+'","client_mutation_id":"1"}}',
            'doc_id': '23863457623296585'
        }
        return payload

class REGPRO5:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = FacebookSession(cookie)
        self.payload_builder = None
        self.ready = False
        self.profile_id = None
    
    def login(self) -> bool:
        self.info = self.session.authenticate()
        if self.info:
            self.payload_builder = GenData(self.session)
            self.ready = True
            return True
        return False
    
    def REG(self, bio: str, name: str) -> tuple:
        """Bước 1: Tạo profile mới"""
        if not self.ready:
            return False, "Not logged in"
        
        payload = self.payload_builder.build(bio, name)
        headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "x-fb-lsd": self.session.lsd,
            "cookie": self.cookie,
            'x-fb-friendly-name': 'AdditionalProfilePlusCreationMutation',
        }
        
        try:
            response = requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=payload)
            response_json = response.json()
            
            if response_json.get('data', {}).get('additional_profile_plus_create', {}).get('error_message'):
                error_msg = response_json['data']['additional_profile_plus_create']['error_message']
                return False, error_msg
            else:
                self.profile_id = response_json['data']['additional_profile_plus_create']['additional_profile']['id']
                return True, self.profile_id
        except Exception as e:
            return False, str(e)
    
    def upload_profile_picture(self, profile_id: str, image_path: str) -> tuple:
        """Bước 2: Upload ảnh đại diện (AVT)"""
        if not self.ready:
            return False, "Not logged in"
        
        headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "cookie": self.cookie,
        }
        
        params = {
            'photo_source': '57',
            'profile_id': profile_id,
            '__user': self.session.user_id,
            '__a': '1',
        }
        
        try:
            with open(image_path, 'rb') as f:
                files = {'source': ('photo.jpg', f, 'image/jpeg')}
                response = requests.post(
                    'https://www.facebook.com/profile/picture/upload/',
                    params=params,
                    headers=headers,
                    cookies=CookieHandler.to_dict(self.cookie),
                    files=files
                )
            return True, response.json()
        except Exception as e:
            return False, str(e)
    
    def upload_cover_photo(self, profile_id: str, image_path: str) -> tuple:
        """Bước 3: Upload ảnh bìa (Cover)"""
        if not self.ready:
            return False, "Not logged in"
        
        headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "cookie": self.cookie,
        }
        
        params = {
            'photo_source': '58',
            'profile_id': profile_id,
            '__user': self.session.user_id,
            '__a': '1',
        }
        
        try:
            with open(image_path, 'rb') as f:
                files = {'source': ('cover.jpg', f, 'image/jpeg')}
                response = requests.post(
                    'https://www.facebook.com/profile/picture/upload/',
                    params=params,
                    headers=headers,
                    cookies=CookieHandler.to_dict(self.cookie),
                    files=files
                )
            return True, response.json()
        except Exception as e:
            return False, str(e)

    def create_full_profile(self, bio: str, name: str, avt_path: str, cover_path: str) -> dict:
        """
        Flow hoàn chỉnh theo đúng thứ tự:
        1. Tạo profile
        2. Upload ảnh đại diện (AVT)
        3. Upload ảnh bìa (Cover)
        4. Hoàn thành - in kết quả
        """
        result = {
            "profile_id": None,
            "avt_uploaded": False,
            "cover_uploaded": False,
            "success": False,
            "errors": []
        }

        # ── Bước 1: Tạo profile ──────────────────────────────────────
        print("[1/3] Đang tạo profile...")
        ok, profile_id = self.REG(bio, name)
        if not ok:
            result["errors"].append(f"Tạo profile thất bại: {profile_id}")
            print(f"  ✗ Thất bại: {profile_id}")
            return result

        result["profile_id"] = profile_id
        print(f"  ✓ Tạo profile thành công | ID: {profile_id}")
        time.sleep(1)

        # ── Bước 2: Upload ảnh đại diện ─────────────────────────────
        print("[2/3] Đang upload ảnh đại diện (AVT)...")
        ok, avt_result = self.upload_profile_picture(profile_id, avt_path)
        if ok:
            result["avt_uploaded"] = True
            print("  ✓ Upload AVT thành công")
        else:
            result["errors"].append(f"Upload AVT thất bại: {avt_result}")
            print(f"  ✗ Upload AVT thất bại: {avt_result}")
        time.sleep(1)

        # ── Bước 3: Upload ảnh bìa ───────────────────────────────────
        print("[3/3] Đang upload ảnh bìa (Cover)...")
        ok, cover_result = self.upload_cover_photo(profile_id, cover_path)
        if ok:
            result["cover_uploaded"] = True
            print("  ✓ Upload ảnh bìa thành công")
        else:
            result["errors"].append(f"Upload ảnh bìa thất bại: {cover_result}")
            print(f"  ✗ Upload ảnh bìa thất bại: {cover_result}")

        # ── Bước 4: Hoàn thành ───────────────────────────────────────
        result["success"] = result["profile_id"] is not None
        print("\n" + "="*45)
        print("         ✅ HOÀN THÀNH TẠO PROFILE")
        print("="*45)
        print(f"  Tên        : {name}")
        print(f"  Bio        : {bio}")
        print(f"  Profile ID : {result['profile_id']}")
        print(f"  AVT        : {'✓ Đã upload' if result['avt_uploaded'] else '✗ Chưa upload'}")
        print(f"  Ảnh bìa    : {'✓ Đã upload' if result['cover_uploaded'] else '✗ Chưa upload'}")
        if result["errors"]:
            print(f"  Lỗi       : {'; '.join(result['errors'])}")
        print("="*45)

        return result


# ── Chạy thử ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    cookie = 'c_user=100005649934250;datr=bQN1aJFhbW4yFLkoinTzHi3d;dpr=0.29520294070243835;sb=bQN1aGlCMhTb78DM9D4H1sYa;xs=8%3AwKkM5xXymUwR8w%3A2%3A1752499126%3A-1%3A-1%3A%3AAcwkH21cmwsqHsDPOnN-YpiPIyDvjw6lEHmWhNNxDA;wd=929x743;fr=0UkuoPE04cqFtjJ9j.AWdqDZMIbJUL1HSC-Dw6l9wDxptr-280CLCjqAK_So5ZWnmbjro.BodQO5..AAA.0.0.Bpf34V.AWcDQ0-XCnn0QwtG1578SdT5B9A;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1769963032201%2C%22v%22%3A1%7D;'

    avt_path   = r'C:\Users\pc\Desktop\shin\telebot\image\avt.jpg'
    cover_path = r'C:\Users\pc\Desktop\shin\telebot\image\cover.jpg'

    manager = REGPRO5(cookie)
    if manager.login():
        print("✓ Đăng nhập thành công\n")
        manager.create_full_profile(
            bio="My bio",
            name="MyPage21",
            avt_path=avt_path,
            cover_path=cover_path
        )
    else:
        print("✗ Đăng nhập thất bại")