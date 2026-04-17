from http import cookies
from wsgiref import headers

import requests

class TTC:
    def __init__(self, token, data, proxy=None):
        self.token = token
        self.data = data
        self.proxy = proxy
        self.cookies = {
            '_fbp': 'fb.1.1761508765559.516195470818743635',
            'PHPSESSID': 'ljug98t3cbp0h74i61u7in71d5',
            '_gid': 'GA1.2.480579025.1775466625',
            '_gcl_au': '1.1.912252535.1775466626',
            '_ga_6RNPVXD039': 'GS2.1.s1775481607$o112$g1$t1775481791$j59$l0$h0',
            '_ga': 'GA1.2.1652707960.1761508764',
            '_gat_gtag_UA_88794877_6': '1',
        }
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'priority': 'u=1, i',
            'referer': 'https://tuongtaccheo.com/kiemtien/likepostvipcheo/',
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            # 'cookie': '_fbp=fb.1.1761508765559.516195470818743635; PHPSESSID=ljug98t3cbp0h74i61u7in71d5; _gid=GA1.2.480579025.1775466625; _gcl_au=1.1.912252535.1775466626; _ga_6RNPVXD039=GS2.1.s1775481607$o112$g1$t1775481791$j59$l0$h0; _ga=GA1.2.1652707960.1761508764; _gat_gtag_UA_88794877_6=1',
        }

    def login(self):
        data = {'access_token': self.token}
        try:
            response = requests.post(
                'https://tuongtaccheo.com/logintoken.php',
                headers={'Content-type': 'application/x-www-form-urlencoded'},
                data=data,
                timeout=15
            )
            
            if response.json().get("status") == "success":
                return response.cookies.get("PHPSESSID")
            else:
                print(f"Check xu thất bại: {response}")
                return None
        except Exception as e:
            print(f"Lỗi khi check xu: {e}")
            return None
        

    def nhapnick(self, phpsessid, iddat):
        cookies = self.cookies
        cookies['PHPSESSID'] = phpsessid
        data = {
            'link': iddat,
            'loainick': 'fb',
        }
        response = requests.post('https://tuongtaccheo.com/cauhinh/nhapnick.php', cookies=cookies, headers=self.headers, data=data).json()
        return response

    def datnick(self, phpsessid, iddat):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            data = {
                'iddat[]': iddat,
                'loai': 'fb',
            }

            response = requests.post('https://tuongtaccheo.com/cauhinh/datnick.php', cookies=cookies, headers=self.headers, data=data).json()
            # response = requests.get('https://tuongtaccheo.com/kiemtien/datnick/getpost.php', cookies=cookies, headers=self.headers).json()
            return response
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None

    def likepostvipcheo(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/likepostvipcheo/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #idfb, idpost,link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None

    def likepostvipre(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/likepostvipre/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #idfb, idpost,link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
        
    def camxucvipcheo(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/camxucvipcheo/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #loaicx idfb, idpost,link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
        
    def camxucvipre(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/camxucvipre/getpost.php', cookies=cookies, headers=self.headers).json()
            return response
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
    def cmtcheo(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/cmtcheo/getpost.php', cookies=cookies, headers=self.headers).json()
            return response # idpost, link, nd "[\"xin giá\",\"rep ib\"
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
    def subcheo(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/subcheo/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #idpost, link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
    def subcheofbvip(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/subcheofbvip/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #idpost, link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
    def sharecheo(self, phpsessid):
        try:
            cookies = self.cookies
            cookies['PHPSESSID'] = phpsessid
            response = requests.get('https://tuongtaccheo.com/kiemtien/sharecheo/getpost.php', cookies=cookies, headers=self.headers).json()
            return response #idpost, link
        except Exception as e:
            print(f"Lỗi khi lấy bài viết: {e}")
            return None
        
    def nhanxu(self,type_job, phpsessid, id_job):
        self.cookies['PHPSESSID'] = phpsessid
        if type_job == "camxucvipre":
            data = {
                'id': id_job,
                'loaicx': 'LOVE',
            }

        if type_job == "camxucvipcheo":
            data = {
                'id': id_job,
                'loaicx': 'LOVE',
            }

        if type_job == "likepostvipre":
            data = {
                'id': id_job,
            }

        if type_job == "likepostvipcheo":
            data = {
                'id': id_job,
            }
        
        if type_job == "cmtcheo":
            data = {
                'id': id_job,
            }

        if type_job == "subcheo":
            data = {
                'id': id_job,
            }

        if type_job == "subcheofbvip":
            data = {
                'id': id_job,
            }
        if type_job == "sharecheo":
            data = {
                'id': id_job,
            }

        response = requests.post(f'https://tuongtaccheo.com/kiemtien/{type_job}/nhantien.php', headers=self.headers,cookies=self.cookies, data=data).json()
        return response
    def run_getjob(self,phpsessid):
         
        if self.data == "likepostvipcheo":
            return self.likepostvipcheo(phpsessid)
        elif self.data == "likepostvipre":
            return self.likepostvipre(phpsessid)
        elif self.data == "camxucvipcheo":
            return self.camxucvipcheo(phpsessid)
        elif self.data == "camxucvipre":
            return self.camxucvipre(phpsessid)
        elif self.data == "cmtcheo":
            return self.cmtcheo(phpsessid)
        elif self.data == "subcheo":
            return self.subcheo(phpsessid)
        elif self.data == "subcheofbvip":
            return self.subcheofbvip(phpsessid)
        elif self.data == "sharecheo":
            return self.sharecheo(phpsessid)
        else:
            print("Loại tương tác không hợp lệ.")
            return None