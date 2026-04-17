import requests
from TDS.API_TDS import TDS
from API_FACEBOOK.api_facebook import FBGRAPHAPI

import json
import re
import requests
import random
import time
import sys
import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import threading

def extract_xu_from_message(msg):
    """Extract XU amount from message like '+400 Xu' or '400'"""
    try:
        match = re.search(r'([\+\-]?\d+)', msg)
        if match:
            return int(match.group(1))
    except:
        pass
    return 0

def parse_proxy(proxy_str):
    """
    Parse proxy string in format 'ip:port:user:pass' or 'ip:port'
    Returns dict for requests library or None if empty
    """
    if not proxy_str or not proxy_str.strip():
        return None
    
    parts = proxy_str.split(':')
    if len(parts) == 2:
        # Format: ip:port
        ip, port = parts
        return {
            'http': f'http://{ip}:{port}',
            'https': f'http://{ip}:{port}'
        }
    elif len(parts) == 4:
        # Format: ip:port:user:pass
        ip, port, user, password = parts
        return {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'http://{user}:{password}@{ip}:{port}'
        }
    return None

class TDS_RUN:
    def __init__(self, data, callbacks=None):
        # self.tds = TDS()
        self.data = data
        self.job_data = {}
        settings = data.get('settings', {})
        self.delay_long = settings.get('delay_long', 60)
        self.delay_short = settings.get('delay_short', 5)
        self.delay_after_tasks = settings.get('delay_after_tasks', 30)
        self.stop_after_tasks = settings.get('stop_after_tasks', 100)
        self.count = {}
        
        # Callbacks for UI updates (thread-safe via QTimer in main.py)
        self.log_callback = callbacks.get('log') if callbacks else None
        self.tree_callback = callbacks.get('tree') if callbacks else None
        self.stats_callback = callbacks.get('stats') if callbacks else None
        self.lock = threading.Lock()
        
        # Global stats
        self.global_stats = {
            'tasks_done': 0,
            'xu_earned': 0,
            'tasks_error': 0
        }

    def update_stats(self, data_tasks):
        """Track task completion and apply delays"""
        job_type = data_tasks['type_job']

        # Ensure job_data[job_type] is always a dict, never overwrite with int
        if job_type not in self.job_data:
            self.job_data[job_type] = {
                "count": 0,
                "status": "running"
            }

        # Safely increment count (check it's a dict first)
        if not isinstance(self.job_data[job_type], dict):
            self.job_data[job_type] = {"count": 0, "status": "running"}
            
        self.job_data[job_type]["count"] += 1
        self.job_data['total'] = self.job_data.get('total', 0) + 1

        delay = random.randint(data_tasks['delay_min'], data_tasks['delay_max'])
        if self.log_callback:
            self.log_callback(f"[⏱] Chờ {delay}s trước task tiếp theo...")
        time.sleep(delay)

        # Check if task type is completed
        if self.job_data[job_type]["count"] >= data_tasks['count']:
            self.job_data[job_type]["status"] = "done"

        # Check if we should do long delay after multiple tasks
        if self.job_data['total'] >= self.delay_after_tasks:
            delay = random.randint(self.delay_short, self.delay_long)
            if self.log_callback:
                self.log_callback(f"[⏳] Đã hoàn thành {self.job_data['total']} nhiệm vụ, nghỉ ngơi {delay}s...")
            time.sleep(delay)

        # Check if we should stop
        if self.job_data['total'] >= self.stop_after_tasks:
            if self.log_callback:
                self.log_callback(f"[🛑] Đã hoàn thành {self.job_data['total']} nhiệm vụ, dừng bot.")
            return True
        
        return False

    def run_tds(self, account):
        tds_user = account['tds_user']
        tds_pass = account['tds_pass']
        tds_token = account['tds_token']
        fb_uid = account['fb_uid']
        fb_token = account['fb_token']
        fb_cookie = account['fb_cookie']
        fb_proxy = account.get('fb_proxy', '')
        
        # Parse proxy
        proxy_dict = parse_proxy(fb_proxy)

        # Log start
        if self.log_callback:
            self.log_callback(f"[→] Bắt đầu chạy: {tds_user}" + (f" (proxy: {fb_proxy})" if fb_proxy else ""))
        
        # Update tree status
        if self.tree_callback:
            self.tree_callback(tds_user, "⏳ Kiểm tra", 0)

        loginfb = FBGRAPHAPI(fb_token, proxies=proxy_dict).get_homepage(fb_cookie)

        if not loginfb:
            if self.log_callback:
                self.log_callback(f"[✘] Đăng nhập Facebook thất bại: {tds_user}")
            if self.tree_callback:
                self.tree_callback(tds_user, "❌ FB lỗi", 0)
            return
        
        if self.log_callback:
            self.log_callback(f"[✔] Đăng nhập Facebook OK: {tds_user}")

        cookie_tds = TDS(tds_token, proxy=proxy_dict).login_tds()

        dat_nick = TDS(tds_token, proxy=proxy_dict).dat_nick(fb_uid)
        if dat_nick.get("error"):
            if TDS(tds_token, proxy=proxy_dict).add_nick(fb_uid, cookie_tds):
                if self.log_callback:
                    self.log_callback(f"[✔] Thêm nick thành công: {tds_user}")
                dat_nick = TDS(tds_token, proxy=proxy_dict).dat_nick(fb_uid)
                if self.log_callback:
                    self.log_callback(f"[→] {dat_nick['data']['msg']}")
        else:
            if self.log_callback:
                self.log_callback(f"[✔] Nick đã config: {dat_nick['data']['msg']}")

        # Update tree status - ready to run
        if self.tree_callback:
            self.tree_callback(tds_user, "⏳ Chạy", 0)

        xu_total = 0
        while True:
            for task in self.data['tasks']:
                if self.tree_callback:
                    self.tree_callback(tds_user, f"⏳ {task['display_name']}", xu_total)
                    
                get_job = TDS(tds_token, proxy=proxy_dict).get_job(task['type_job'])
                if self.log_callback:
                    self.log_callback(f"[→] Lấy job {task['display_name']}: {len(get_job.get('data', []))} task")
                try:
                    if len(get_job['data']) > 0:
                        
                        for job in get_job['data']:
                            if self.job_data.get(task['type_job'], {}).get('status') == 'done':
                                if self.log_callback:
                                    self.log_callback(f"[→] Nhiệm vụ {task['display_name']} đã hoàn thành, bỏ qua...")
                                break
                            if task['type_job'] == "facebook_reaction" or task['type_job'] == "facebook_reaction2":
                                if job['type'] == "LIKE":
                                    re = FBGRAPHAPI(fb_token, proxies=proxy_dict).FB_LIKES(job['id'])
                                else:
                                    re = FBGRAPHAPI(fb_token, proxies=proxy_dict, data_homepage=loginfb, cookie=fb_cookie).FB_REACTION(job['id'], job['type'])
                                if re:
                                    nhanxu = TDS(tds_token, proxy=proxy_dict).get_coin(task["type_job"], job['code'])
                                    if nhanxu.get('success') == 200:
                                        xu_gained = extract_xu_from_message(nhanxu['data'].get('msg', ''))
                                        xu_total += xu_gained
                                        if self.log_callback:
                                            self.log_callback(f"[✔] {task['display_name']}: {nhanxu['data']['msg']} | Tổng: {xu_total}")
                                        # Update stats
                                        self.global_stats['tasks_done'] += 1
                                        self.global_stats['xu_earned'] = xu_total
                                        if self.stats_callback:
                                            self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])
                                        # Update tree
                                        if self.tree_callback:
                                            self.tree_callback(tds_user, f"⏳ {task['display_name']}", xu_total)
                                        if self.update_stats(task): 
                                            if self.tree_callback:
                                                self.tree_callback(tds_user, "✅ Hoàn thành", xu_total)
                                            return
                                    else:
                                        self.global_stats['tasks_error'] += 1
                                        if self.log_callback:
                                            self.log_callback(f"[✘] Nhận xu thất bại: {nhanxu.get('error', 'Unknown')}")
                                        if self.stats_callback:
                                            self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])

                            elif task['type_job'] == "facebook_follow":
                                re = FBGRAPHAPI(fb_token, proxies=proxy_dict).FB_FOLLOW(job['id'])
                                if re:
                                    post = TDS(tds_token, proxy=proxy_dict).post_job('facebook_follow_cache', job['code'])
                                    if self.log_callback:
                                        self.log_callback(f"[→] Post job {task['display_name']}: cache={post.get('cache', 0)}")
                            elif task['type_job'] == "facebook_share":
                                re = FBGRAPHAPI(fb_token, proxies=proxy_dict).FB_SHARE(job['id'])
                                if re:
                                    nhanxu = TDS(tds_token, proxy=proxy_dict).get_coin(task["type_job"], job['code'])
                                    if nhanxu.get('success') == 200:
                                        xu_gained = extract_xu_from_message(nhanxu['data'].get('msg', ''))
                                        xu_total += xu_gained
                                        if self.log_callback:
                                            self.log_callback(f"[✔] {task['display_name']}: {nhanxu['data']['msg']} | Tổng: {xu_total}")
                                        self.global_stats['tasks_done'] += 1
                                        self.global_stats['xu_earned'] = xu_total
                                        if self.stats_callback:
                                            self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])
                                        if self.tree_callback:
                                            self.tree_callback(tds_user, f"⏳ {task['display_name']}", xu_total)
                                        if self.update_stats(task): 
                                            if self.tree_callback:
                                                self.tree_callback(tds_user, "✅ Hoàn thành", xu_total)
                                            return
                                    else:
                                        self.global_stats['tasks_error'] += 1
                                        if self.log_callback:
                                            self.log_callback(f"[✘] Nhận xu thất bại: {nhanxu.get('error', 'Unknown')}")
                                        if self.stats_callback:
                                            self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])

                        if task['type_job'] == "facebook_follow":
                            nhanxu = TDS(tds_token, proxy=proxy_dict).get_coin(task["type_job"], "facebook_api")
                            if nhanxu.get('success') == 200:
                                xu_gained = extract_xu_from_message(nhanxu['data'].get('msg', ''))
                                xu_total += xu_gained
                                if self.log_callback:
                                    self.log_callback(f"[✔] {task['display_name']}: {nhanxu['data']['msg']} | Tổng: {xu_total}")
                                self.global_stats['tasks_done'] += 1
                                self.global_stats['xu_earned'] = xu_total
                                if self.stats_callback:
                                    self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])
                                if self.tree_callback:
                                    self.tree_callback(tds_user, "✅ Theo dõi", xu_total)
                                if self.update_stats(task): 
                                    return
                            else:
                                self.global_stats['tasks_error'] += 1
                                if self.log_callback:
                                    self.log_callback(f"[✘] Nhận xu {task['display_name']} thất bại: {nhanxu.get('error', 'Unknown')}")
                                if self.stats_callback:
                                    self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])
                    else:
                        if self.log_callback:
                            self.log_callback(f"[→] Không có task {task['display_name']}, chờ {self.delay_short}s...")
                        time.sleep(self.delay_short)
                except Exception as e:
                    self.global_stats['tasks_error'] += 1
                    if self.log_callback:
                        self.log_callback(f"[✘] Exception: {str(e)}")
                    if self.tree_callback:
                        self.tree_callback(tds_user, "❌ Lỗi", xu_total)
                    if self.stats_callback:
                        self.stats_callback(self.global_stats['tasks_done'], self.global_stats['xu_earned'], self.global_stats['tasks_error'])
                    if get_job.get('error'):
                        if self.log_callback:
                            self.log_callback(f'[✘] Lỗi get job: {get_job["error"]}')
                        time.sleep(self.delay_short)
                    if get_job.get('countdown'):
                        if self.log_callback:
                            self.log_callback(f'[⌛] Countdown: {get_job["countdown"]}s')
                        time.sleep(get_job['countdown'])

    def main(self):
        for account in self.data['accounts']:
            thread = threading.Thread(target=self.run_tds, args=(account,))
            thread.start()