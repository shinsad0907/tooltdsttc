from os import link
from urllib import response
import requests, json, uuid, re
import requests, sys, json, time

class FBGRAPHAPI:
    def __init__(self, fb_token, data_homepage=None, proxies=None, cookie=None):
        self.fb_token = fb_token
        self.baseurl = "https://graph.facebook.com/"
        self.proxies = proxies or None
        self.cookie = cookie
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'cache-control': 'max-age=0',
            'dpr': '1',
            'priority': 'u=0, i',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-full-version-list': '"Google Chrome";v="141.0.7390.123", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'viewport-width': '567',
        }
        try:
            self.dtsg = data_homepage.get('dtsg', '')
            self.jazoest = data_homepage.get('jazoest', '')
            self.av = data_homepage.get('av', '')
        except:
            pass


    def get_homepage(self, cookie):
        headers = self.headers.copy()
        headers['cookie'] = cookie
        try:
            response = requests.get('https://www.facebook.com', headers=headers).text
            self.dtsg = response.split('{"dtsg":{"token":"')[1].split('"')[0]
            self.jazoest = response.split('jazoest=')[1].split('"')[0]
            self.av = cookie.split('c_user=')[1].split(';')[0]
            return {
                'dtsg': self.dtsg,
                'jazoest': self.jazoest,
                'av': self.av
            }
        except Exception as e:
            return False

    def GetPro5(self):
        try:
            url = f"https://graph.facebook.com/me/accounts?access_token={self.fb_token}"
            response = requests.get(url, proxies=self.proxies)
            if response.status_code == 200:
                return response.json()
            else:
                return False
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            return False
    def FB_REACTION(self, id, cx="LOVE"):
        reaction_map = {
            'LOVE': '1678524932434102',
            'HAHA': '115940658764963',
            'WOW': '478547315650144',
            'SAD': '908563459236466',
            'ANGRY': '444813342392137',
            'CARE': '613557422527858'
        }
        feedback_reaction_id = reaction_map.get(cx, '1678524932434102')
        try:
            headers_get = self.headers.copy()
            headers_get['cookie'] = self.cookie
            
            response_text = requests.get(
                f'https://www.facebook.com/{id}', 
                headers=headers_get
            ).text

            # Parse feedback_id
            try:
                feedback_id = response_text.split('"feedback":{"id":"')[1].split('"')[0]
            except:
                try:
                    feedback_id = response_text.split('{"associated_group":null,"id":"')[1].split('"')[0]
                except:
                    print("Không parse được feedback_id")
                    return False

            # Parse lsd token
            lsd_match = re.search(r'"LSD",\[\],\{"token":"([^"]+)"\}', response_text)
            lsd_token = lsd_match.group(1) if lsd_match else ""

            print(f"Feedback ID: {feedback_id} | LSD: {lsd_token}")

            headers_action = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.facebook.com',
                'referer': f'https://www.facebook.com/{id}',
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'x-asbd-id': '359341',
                'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
                'x-fb-lsd': lsd_token,  # thêm
                'cookie': self.cookie,
            }

            variables = {
                "input": {
                    "attribution_id_v2": f"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,{int(time.time()*1000)},819514,,,",
                    "feedback_id": feedback_id,
                    "feedback_reaction_id": feedback_reaction_id,
                    "feedback_source": "OBJECT",
                    "is_tracking_encrypted": True,
                    "tracking": [""],
                    "session_id": str(uuid.uuid4()),
                    "downstream_share_session_id": str(uuid.uuid4()),
                    "downstream_share_session_origin_uri": f"https://www.facebook.com/{id}",
                    "downstream_share_session_start_time": str(int(time.time() * 1000)),
                    "actor_id": self.av,
                    "client_mutation_id": "1"
                },
                "useDefaultActor": False,
                "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False
            }

            data = {
                'av': self.av,
                '__user': self.av,   # thêm
                '__a': '1',          # thêm
                'fb_dtsg': self.dtsg,
                'jazoest': self.jazoest,
                'lsd': lsd_token,    # thêm
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
                'server_timestamps': 'true',
                'variables': json.dumps(variables),
                'doc_id': '34830500936594656',
            }

            response = requests.post(
                'https://www.facebook.com/api/graphql/',
                headers=headers_action,
                data=data
            )
            print(response.text)
            result = response.json()
            return result.get('extensions', {}).get('is_final', False)
        except Exception as e:
            print(f"Lỗi: {e}")
            return False
    def FB_LIKES(self,id):
        try:
            url = self.baseurl + f"{id}/likes"
            params = {
                'access_token':self.fb_token
            }
            r = requests.post(url, params=params, proxies=self.proxies)
            print(r.json())
            if r.status_code == 200:
                if r.json() == True:
                    return True
                else :
                    return False
            else:
                print(r.json())
                return False
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            return False
    def FB_SHARE(self, post_id):
        try:
            post_url = f"https://m.facebook.com/{post_id}"
            url = f"{self.baseurl}me/feed"
            params = {
                'method': 'POST',
                'link': post_url,
                'published': '1',
                'access_token': self.fb_token
            }
            response = requests.post(url, params=params, proxies=self.proxies)
            print(response.text)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f"Profile Error: {e}")
            return False
        except Exception as e:
            print(f"Profile Error: {e}")
            return False
    def FB_COMMENTS(self,id,cmt):
        try:
            url = self.baseurl + f"{id}/comments"
            params = {
                'message' : cmt,
                'access_token':self.fb_token
            }
            r = requests.post(url, params=params, proxies=self.proxies)
            

            if r.status_code == 200:
                return True
            else:
                return False
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            return False
        
    def FB_FOLLOW(self,id):
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.facebook.com',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'x-asbd-id': '359341',
                'x-fb-friendly-name': 'CometUserFollowMutation',
                'cookie': self.cookie,
            }
            data = {
                'av': self.av,
                'fb_dtsg': self.dtsg,
                'jazoest': self.jazoest,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'CometUserFollowMutation',
                'server_timestamps': 'true',
                'variables': '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,1761770333439,296769,250100865708545,,","is_tracking_encrypted":false,"subscribe_location":"PROFILE","subscribee_id":'+f"{id}"+',"tracking":null,"actor_id":'+f"{self.av}"+',"client_mutation_id":"5"},"scale":1}',
                'doc_id': '24860303246962259',
            }
            response = requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=data).json()
            return response.get('extensions', {}).get('is_final', False)
        except:
            return False
        
    def FB_RUN(self, type_task, id,cx= None, cmt=None):
        print(f"Running task: {type_task} | ID: {id} | Reaction: {cx} | Comment: {cmt}")
        if type_task == "likepostvipcheo":
            self.FB_LIKES(id)
        elif type_task == "likepostvipre":
            self.FB_LIKES(id)
        elif type_task == "camxucvipre":
            self.FB_REACTION(id, cx)
        elif type_task == "camxucvipcheo":
            self.FB_REACTION(id, cx)
        elif type_task == "sharecheo":
            self.FB_SHARE(id)
        elif type_task == "cmtcheo":
            self.FB_COMMENTS(id, cmt)
        elif type_task == "subcheofbvip":
            self.FB_FOLLOW(id)
        elif type_task == "subcheo":
            self.FB_FOLLOW(id)
        return True
    
# FBGRAPHAPI('EAAD6V7os0gcBRBfZBd2FswZAFkZCllAsoJFyzm1JuTl2fvIygoZCM6lWW8R5N81GtQgd51jFCn374ADbGZBXjsDZCqzQGUx2WpRZAZCXHZC9t7r0PJ1s5sCfsNY9DXQTcsv7e0LfZCOpnBaO3VPqdcKKZAY576Wuejup8KpIoh03geKDcDeMla5mnVZBMOmbJfK8ZASWGP1NisGcutgZDZD').FB_LIKES('681630921505469',)