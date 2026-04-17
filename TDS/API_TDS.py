from time import sleep
import requests

class TDS:
    def __init__(self, token, proxy=None):
        self.CAPTCHA_CLIENT_KEY = "0947ca39d6d344a0a6849b678144f7ad"
        self.CAPTCHA_WEBSITE_URL = "https://traodoisub.com/"
        self.CAPTCHA_SITE_KEY = "6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a"    
        self.proxy = proxy
    
        self.cookies = {
            'cf_clearance': 'qzzLbqUR1jbVznKdQI1VRf1hFsZhQJV44qmdE9DSygM-1761602690-1.2.1.1-z8ZDhDlQKdlyIOduDTWwjbU7MP6lZ1z7OtmJApoPF6ViZV2NSvCZHOfJFrlh8ahAIoYWAj0DHqmiTnmodpRPYyW.dRvtgtTRRvOOk86NTFgR4Bp47IjL20f2oGmQwHdY94HjkI9eqdbMixuKB6ZBeZspZDC8w1LdRKWBhrEWcN1myl8UtFgae5fO4POPVMOTHprdbcb7UcgZssq1_r9a3xbuzsQAdgaPKyYK9wUGGl0',
            'PHPSESSID': 'c1ebb08a8b73157f3e72790717606c36',
        }
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://traodoisub.com',
            'priority': 'u=1, i',
            'referer': 'https://traodoisub.com/view/cauhinh/',
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.token = token
        self.url = "https://traodoisub.com/api/"
        # self.data = data

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


    def login_tds(self):
        re = requests.get(f"{self.url}?fields=profile&access_token={self.token}")
        if re.json().get("error"):
            return re.json().get("error")
        return re.cookies.get("PHPSESSID")
    
    def add_nick(self, idfb, cookie):
        cookies = self.cookies.copy()
        cookies['PHPSESSID'] = cookie

        token = self.solve_recaptcha_v2()

        if not token:
            print("Không thể lấy token reCAPTCHA.")
            return None

        data = {
            'idfb': idfb,
            'g-recaptcha-response': token
        }

        response = requests.post('https://traodoisub.com/scr/add_uid.php', cookies=cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            return  True
        else:
            print(f"Thêm nick thất bại: {response.text}")
            return False
        
        
    def dat_nick(self, idfb):
        re = requests.get(f"{self.url}?fields=run&id={idfb}&access_token={self.token}").json()
        return re #{error} {
                        # "success": 200,
                        # "data": {
                        #     "id": "100006177545047",
                        #     "msg": "Cấu hình thành công!"
                        # }
                        # }

    def get_job(self, type_job):
        re = requests.get(f"{self.url}?fields={type_job}&access_token={self.token}").json()
        return re 
        # {
        #     "cache": 0,
        #     "data": [
        #         {
        #         "id": "100064877612993_980823404090238",
        #         "code": "WSE9W9VGJQFP5TG28RC5",
        #         "type": "LIKE"
        #         }
        #     ]
        # }
    
    def post_job(self, type_job, id_job):
        re = requests.get(f"{self.url}coin/?type={type_job}&id={id_job}&access_token={self.token}").json()
        return re # Bao gồm: facebook_follow_cache, facebook_page_cache
        # {
        #     "cache":1     //cache là số nhiệm vụ chưa nhận xu, trên 4 nhiệm vụ có thể nhận xu
        # }

    def get_coin(self, type_job, id_job):
        re = requests.get(f"{self.url}coin/?type={type_job}&id={id_job}&access_token={self.token}").json()
        return re #code nhiệm vũ đã làm. Riêng facebook_follow, facebook_page mặc định là facebook_api
        {
        "success": 200,
        "data": {
            "xu": 560274200,
            "job_success": 2,
            "xu_them": 4200,
            "msg": "+4200 Xu"
        }
        }


# print(TDS("token").dat_nick("likepostvipcheo"))