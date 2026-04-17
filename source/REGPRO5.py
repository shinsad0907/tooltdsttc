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
                "lsd" : self.lsd or "N/A",
            }
        except Exception as e:
            return False

        
class GenData:
    def __init__(self, session: FacebookSession):
        self.session = session
        self.request_counter = 0
    
    def build(self, bio: str, name: str) -> Dict[str, Any]:
        self.request_counter += 1   
        category_id = [169421023103905,2347428775505624,2347428775505624,2347428775505624,192614304101075,145118935550090,1350536325044173,471120789926333,180410821995109,145118935550090,357645644269220,2705]
        category=random.choice(category_id) 
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
            "lsd" : self.session.lsd,
            'variables': '{"input":{"bio":"'+bio+'","categories":["'+str(category)+'"],"creation_source":"comet","name":"'+name+'","off_platform_creator_reachout_id":null,"page_referrer":"launch_point","actor_id":"'+self.session.user_id+'","client_mutation_id":"1"}}',
            'doc_id' : '23863457623296585'
          
        }
        return payload
class REGPRO5:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = FacebookSession(cookie)
        self.payload_builder = None
        self.ready = False
    def login(self) -> bool:
        self.info = self.session.authenticate()
        if self.info:
            self.payload_builder = GenData(self.session)
            self.ready = True
            return True
       
    def REG(self, bio: str, name: str) -> Dict[str, Any]:
        if not self.ready:
            return {"success": False, "error": "Not logged in"}
        payload = self.payload_builder.build(bio,name)
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
            "cookie" : self.cookie,
            'x-fb-friendly-name': 'AdditionalProfilePlusCreationMutation',
        }
        try:
            response = requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=payload, timeout=30)
            resp_json = response.json()
            
            # Handle GraphQL errors
            if "errors" in resp_json and resp_json["errors"]:
                error_msg = resp_json["errors"][0].get("message", "Unknown error")
                return {"ok": False, "error": error_msg}
            
            # Handle missing data key
            if "data" not in resp_json:
                return {"ok": False, "error": "Invalid response from FB"}
            
            data = resp_json.get("data", {})
            reg_result = data.get("additional_profile_plus_create", {})
            
            # Check for error_message field
            if reg_result.get("error_message"):
                return {"ok": False, "error": reg_result["error_message"]}
            
            # Success - extract page ID
            profile = reg_result.get("additional_profile", {})
            page_id = profile.get("id")
            
            if page_id:
                return {"ok": True, "page_id": page_id, "name": name}
            else:
                return {"ok": False, "error": "No page ID in response"}
        
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": f"Request error: {str(e)}"}
        except ValueError as e:
            return {"ok": False, "error": f"JSON parse error: {str(e)}"}
        except Exception as e:
            return {"ok": False, "error": f"Unexpected error: {str(e)}"}
