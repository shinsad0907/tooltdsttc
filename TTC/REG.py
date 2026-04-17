import requests
from time import sleep
import random
import string

class RegTDS:
    def __init__(self):
        self.CAPTCHA_CLIENT_KEY = "0947ca39d6d344a0a6849b678144f7ad"
        self.CAPTCHA_WEBSITE_URL = "https://traodoisub.com/"
        self.CAPTCHA_SITE_KEY = "6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a"
        self.tokentds = None

        self.cookies = {
            'cf_clearance': 'qzzLbqUR1jbVznKdQI1VRf1hFsZhQJV44qmdE9DSygM-1761602690-1.2.1.1-z8ZDhDlQKdlyIOduDTWwjbU7MP6lZ1z7OtmJApoPF6ViZV2NSvCZHOfJFrlh8ahAIoYWAj0DHqmiTnmodpRPYyW.dRvtgtTRRvOOk86NTFgR4Bp47IjL20f2oGmQwHdY94HjkI9eqdbMixuKB6ZBeZspZDC8w1LdRKWBhrEWcN1myl8UtFgae5fO4POPVMOTHprdbcb7UcgZssq1_r9a3xbuzsQAdgaPKyYK9wUGGl0',
        }
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://traodoisub.com',
            'priority': 'u=1, i',
            'referer': 'https://traodoisub.com/',
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

    def tao_chuoi_ngau_nhien(self, do_dai=8):
        ky_tu = string.ascii_letters + string.digits
        return ''.join(random.choice(ky_tu) for _ in range(do_dai))

    def solve_recaptcha_v2(self):
        try:
            create_payload = {
                "clientKey": self.CAPTCHA_CLIENT_KEY,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": self.CAPTCHA_WEBSITE_URL,
                    "websiteKey": self.CAPTCHA_SITE_KEY,
                }
            }

            r = requests.post(
                "https://api.3xcaptcha.com/createTask",
                json=create_payload,
                timeout=30
            ).json()

            if r.get("errorId") != 0:
                raise Exception(f"CreateTask failed: {r.get('errorDescription', 'Unknown error')}")

            task_id = r["taskId"]
            print(f"Task ID: {task_id}")
            sleep(10)

            for attempt in range(1, 25):
                print(f"Polling lần {attempt}...")
                res = requests.post(
                    "https://api.3xcaptcha.com/getTaskResult",
                    json={"clientKey": self.CAPTCHA_CLIENT_KEY, "taskId": task_id},
                    timeout=30
                ).json()

                status = res.get("status")
                if status == "ready":
                    print("Lấy token thành công!")
                    return res["solution"]["gRecaptchaResponse"]
                elif status == "processing":
                    sleep(5)
                else:
                    raise Exception(f"Task failed: {res.get('errorDescription', res)}")

            raise Exception("Timeout: Không nhận được kết quả sau 2 phút")

        except Exception as e:
            print(f"Lỗi solve captcha: {e}")
            return None

    def login(self, username: str, password: str):
        data = {
            'username': username,
            'password': password,
        }
        response = requests.post(
            'https://traodoisub.com/scr/login.php',
            cookies=self.cookies,
            headers=self.headers,
            data=data
        )
        if response.json().get("success"):
            return response.cookies.get('PHPSESSID')  # ✅ Dùng .get() an toàn hơn
        else:
            print(f"Đăng nhập thất bại: {response.json()}")
            return None

    def get_token(self, phpsessid: str):  # ✅ Đổi tên tham số cho rõ ràng
        cookies = self.cookies.copy()
        cookies['PHPSESSID'] = phpsessid  # ✅ Sửa bug: gán đúng giá trị
        response = requests.get(
            'https://traodoisub.com/view/setting/load.php',
            cookies=cookies,
            headers=self.headers
        ).json()
        return response.get("tokentds")

    def REG(self):
        tai_khoan = self.tao_chuoi_ngau_nhien(10)
        mat_khau = self.tao_chuoi_ngau_nhien(12)
        token = self.solve_recaptcha_v2()

        if not token:
            print("Không thể lấy token reCAPTCHA.")
            return None

        print(f"Token reCAPTCHA: {token[:30]}...")
        data = {
            'dkusername': tai_khoan,
            'dkpassword': mat_khau,
            'rdkpassword': mat_khau,
            'g-recaptcha-response': token,
        }

        response = requests.post(
            'https://traodoisub.com/scr/check_reg.php',
            cookies=self.cookies,
            headers=self.headers,
            data=data
        ).json()

        if response.get("success"):
            return {"username": tai_khoan, "password": mat_khau}
        else:
            print(f"Đăng ký thất bại: {response}")
            return None

    def run(self):
        account_info = self.REG()
        if not account_info:
            print("Đăng ký không thành công.")
            return None

        phpsessid = self.login(account_info["username"], account_info["password"])
        if not phpsessid:
            return None

        self.tokentds = self.get_token(phpsessid)
        return {
            "username": account_info["username"],
            "password": account_info["password"],
            "tokentds": self.tokentds,
        }

class Checkxu:
    """Check xu từ tuongtaccheo.com."""
    def __init__(self, token):
        self.token = token
        self.headers = {'Content-type': 'application/x-www-form-urlencoded'}

    def checkxu(self):
        data = {'access_token': self.token}
        try:
            response = requests.post(
                'https://tuongtaccheo.com/logintoken.php',
                headers=self.headers,
                data=data,
                timeout=15
            ).json()
            
            if response.get("status") == "success":
                # Lấy sodu từ data
                if isinstance(response.get('data'), dict):
                    return response['data'].get("sodu")
                elif 'sodu' in response:
                    return response.get("sodu")
            return None
        except Exception:
            return None
        
# print(Checkxu("2bed5421f5de3979067f81bd36c0dbb5").checkxu())