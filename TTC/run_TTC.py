import json
import re
import requests
import random
import time
import sys
import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from API_FACEBOOK.api_facebook import FBGRAPHAPI
from TTC.API_TTC import TTC
import threading

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


class RUN_TTC:
    def __init__(self, data, callbacks=None):
        self.data = data
        # Handle both old format (top-level settings) and new format (nested 'settings')
        settings = data.get('settings', data)
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
        self.stop_flag = False  # Flag to stop execution
        
        # Global stats
        self.global_stats = {
            'tasks_done': 0,
            'xu_earned': 0,
            'tasks_error': 0
        }
    
    def _log(self, msg):
        """Write log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        if self.log_callback:
            self.log_callback(log_msg)
    
    def _update_tree(self, ttc_user, status, xu):
        print(f"Update tree: {ttc_user} | Status: {status} | Xu: {xu}")
        """Update tree item for account"""
        if self.tree_callback:
            self.tree_callback(ttc_user, status, xu)
    
    def _update_stats(self, tasks_done=None, xu_earned=None, tasks_error=None):
        """Update global stats"""
        with self.lock:
            if tasks_done is not None:
                self.global_stats['tasks_done'] = tasks_done
            if xu_earned is not None:
                self.global_stats['xu_earned'] = xu_earned
            if tasks_error is not None:
                self.global_stats['tasks_error'] = tasks_error
            
            if self.stats_callback:
                self.stats_callback(
                    self.global_stats['tasks_done'],
                    self.global_stats['xu_earned'],
                    self.global_stats['tasks_error']
                )
    
    def _all_tasks_done(self):
        """Check if all tasks have been completed"""
        for task in self.data.get('tasks', []):
            task_type = task.get('type_job')
            if not task_type:
                continue
            task_status = self.count.get(task_type, {}).get("status")
            if task_status != "done":
                return False
        return True
    
    def stop(self):
        """Signal to stop execution"""
        self.stop_flag = True
        self._log("🛑 Người dùng yêu cầu dừng...")
    
    def status_run(self, ttc_user, task_type, account_total_xu):
        """Check task status, log delays, update tree - return (should_break, reason)"""
        # Initialize task_type as dict if not exists
        if task_type not in self.count:
            self.count[task_type] = {"count": 0, "status": "running"}
        elif not isinstance(self.count[task_type], dict):
            self.count[task_type] = {"count": 0, "status": "running"}
        
        self.count[task_type]["count"] += 1
        self.count['total'] = self.count.get('total', 0) + 1
        self.count['total_after_tasks'] = self.count.get('total_after_tasks', 0) + 1
        
        task = next((t for t in self.data['tasks'] if t['type_job'] == task_type), None)
        if not task:
            return False, 'continue'
        
        # Task delay (between tasks of same type)
        delay = random.randint(task['delay_min'], task['delay_max'])
        self._log(f"│    ⏳ Delay nhiệm vụ {delay}s...")
        self._update_tree(ttc_user, f"⏳ Chờ {delay}s", str(account_total_xu))
        time.sleep(delay)
        
        # Check if task type reached its limit
        if self.count[task_type]["count"] >= task['count']:
            self._log(f"│    🎉 Đã hoàn thành tất cả {task['count']} task của {task['display_name']}")
            self.count[task_type]["status"] = "done"
            return True, 'job_done'
        
        # Check if total tasks reached global limit
        if self.count['total'] >= self.data['stop_after_tasks']:
            self._log(f"└─ ✅ Đã tích lũy {self.count['total']}/{self.stop_after_tasks} tasks tổng cộng")
            return True, 'run_done'
        
        # Check if need long delay between task batches
        if self.count['total_after_tasks'] >= self.delay_after_tasks:
            long_delay = random.randint(self.delay_short, self.delay_long)
            self._log(f"│    ⏳ PAUSE {long_delay}s (đã làm {self.count['total_after_tasks']} tasks, chuyển task khác)")
            self._update_tree(ttc_user, f"⏳ PAUSE {long_delay}s", str(account_total_xu))
            time.sleep(long_delay)
            self.count['total_after_tasks'] = 0 
        
        return False, 'continue'
    def run_ttc(self, acc):
        ttc_user = acc.get('ttc_user', 'Unknown')
        fb_uid = acc.get('fb_uid', 'Unknown')
        fb_proxy = acc.get('fb_proxy', '')
        
        # Parse proxy
        proxy_dict = parse_proxy(fb_proxy)
        
        self._log(f"==================== START: {ttc_user} ====================")
        self._log(f"📱 TTC: {ttc_user} | FB: {fb_uid}" + (f" | Proxy: {fb_proxy}" if fb_proxy else ""))
        self._update_tree(ttc_user, "⏳ Đăng nhập...", "0")
        
        try:
            # Step 1: Login
            self._log(f"[1/4] Đang đăng nhập TTC...")
            PHPSESSID = TTC(acc['ttc_token'], "likepostvipcheo", proxy=proxy_dict).login()
            if not PHPSESSID:
                self._log(f"❌ Lỗi login TTC")
                self._log(f"❌ Ngưng chạy tài khoản {ttc_user}")
                self._update_tree(ttc_user, "❌ Login thất bại", "0")
                self._log(f"==================== STOP: {ttc_user} (Login failed) ====================\n")
                self.global_stats['tasks_error'] += 1
                self._update_stats(tasks_error=self.global_stats['tasks_error'])
                return
            self._log(f"✅ Đăng nhập TTC thành công")
            self._update_tree(ttc_user, "⏳ Lấy FB data...", "0")
            
            # Step 2: Get Facebook homepage data
            self._log(f"[2/4] Đang lấy dữ liệu Facebook...")
            datahomepage = FBGRAPHAPI(acc['fb_token'], proxies=proxy_dict, data_homepage=None, cookie=acc['fb_cookie']).get_homepage(acc['fb_cookie'])
            if not datahomepage:
                self._log(f"❌ Không thể lấy dữ liệu Facebook")
                self._log(f"❌ Ngưng chạy tài khoản {ttc_user}")
                self._update_tree(ttc_user, "❌ FB data lỗi", "0")
                self._log(f"==================== STOP: {ttc_user} (FB data failed) ====================\n")
                self.global_stats['tasks_error'] += 1
                self._update_stats(tasks_error=self.global_stats['tasks_error'])
                return
            self._log(f"✅ Đã lấy dữ liệu Facebook")
            self._update_tree(ttc_user, "⏳ Cấu hình nick...", "0")
            
            # Step 3: Check/Set nick
            self._log(f"[3/4] Đang kiểm tra nick FB...")
            datnick = TTC(acc['ttc_token'], "likepostvipcheo", proxy=proxy_dict).datnick(PHPSESSID, acc['fb_uid'])
            time.sleep(5)
            self._log(f"📋 Kết quả datnick: {datnick}")
            
            if int(datnick) != 1:
                self._log(f"⚠️  Nick chưa được đặt, đang cấu hình...")
                nhapnick = TTC(acc['ttc_token'], "likepostvipcheo", proxy=proxy_dict).nhapnick(PHPSESSID, acc['fb_uid'])
                self._log(f"📋 Kết quả nhapnick: {nhapnick}")
                time.sleep(5)
                
                if int(nhapnick) == 1:
                    self._log(f"✅ Đã nhập nick {fb_uid} thành công")
                    datnick = TTC(acc['ttc_token'], "likepostvipcheo", proxy=proxy_dict).datnick(PHPSESSID, acc['fb_uid'])
                    time.sleep(5)
                else:
                    self._log(f"❌ Nhập nick thất bại - không đủ điều kiện")
                    self._log(f"❌ Ngưng chạy tài khoản {ttc_user}")
                    self._update_tree(ttc_user, "❌ Setup nick failed", "0")
                    self._log(f"==================== STOP: {ttc_user} (Nick setup failed) ====================\n")
                    self.global_stats['tasks_error'] += 1
                    self._update_stats(tasks_error=self.global_stats['tasks_error'])
                    return
            else:
                self._log(f"✅ Nick {fb_uid} đã được đặt")
            
            self._update_tree(ttc_user, "⏳ Đang chạy tasks...", "0")
            self._log(f"[4/4] Bắt đầu vòng lặp nhiệm vụ...")
            
            account_total_xu = 0
            account_tasks_done = 0
            account_tasks_error = 0
            
            while True:
                # Check if stop flag is set
                if self.stop_flag:
                    self._log(f"└─ 🛑 Người dùng đã dừng, thoát acc {ttc_user}")
                    self._update_tree(ttc_user, "🛑 Đã dừng", str(account_total_xu))
                    self._log(f"==================== STOP: {ttc_user} ====================")
                    self._log(f"📊 Tổng kết: Done={account_tasks_done}, Xu={account_total_xu}, Error={account_tasks_error}\n")
                    return
                
                for task in self.data['tasks']:
                    self._log(f"┌─ Lấy jobs cho task: {task['display_name']} ({task['type_job']})")
                    
                    get_jobs = TTC(acc['ttc_token'], task['type_job'], proxy=proxy_dict).run_getjob(PHPSESSID)
                    self._log(f"│  API Response: {str(get_jobs)[:100]}...")
                    get_jobs = json.loads(get_jobs) if isinstance(get_jobs, str) else get_jobs
                    
                    # Check if API returned error
                    if isinstance(get_jobs, dict) and 'error' in get_jobs:
                        countdown = get_jobs.get('countdown', 0)
                        self._log(f"│  ⚠️  Rate limit: {get_jobs['error']} - Chờ {countdown}s")
                        if countdown > 0:
                            time.sleep(countdown)
                        account_tasks_error += 1
                        continue
                    
                    # If not a list, skip
                    if not isinstance(get_jobs, list):
                        self._log(f"│  ❌ Lỗi: Response không phải list - {type(get_jobs)}")
                        account_tasks_error += 1
                        continue
                    
                    self._log(f"│  📊 Tìm thấy {len(get_jobs)} jobs")
                    
                    for job_idx, job in enumerate(get_jobs, 1):
                        if self.count.get(task['type_job'], {}).get("status") == "done":
                            break
                        countdown = job.get("countdown", 0)
                        if countdown > 0:
                            self._log(f"│  ⏱️  Job #{job_idx}: Countdown {countdown}s - Bỏ qua")
                            continue
                        
                        # Extract ID
                        if task['type_job'] in ['likepostvipcheo', 'likepostvipre', 'camxucvipcheo', 'camxucvipre']:
                            idpost = job.get('idfb', '')
                        else:
                            idpost = job.get('idpost', '')
                        
                        loaicx = job.get('loaicx', '')
                        nd = job.get('nd', '')
                        
                        # Update status với task đang làm
                        task_display = task['display_name'][:12]
                        self._update_tree(ttc_user, f"⏳ {task_display}...", str(account_total_xu))
                        
                        # Execute action
                        status_action = FBGRAPHAPI(acc['fb_token'], proxies=proxy_dict, data_homepage=datahomepage, cookie=acc['fb_cookie']).FB_RUN(
                            task['type_job'], idpost, loaicx, nd
                        )
                        
                        if status_action:
                            # Get reward
                            nhantien = TTC(acc['ttc_token'], task['type_job'], proxy=proxy_dict).nhanxu(task['type_job'], PHPSESSID, job['idpost'])
                            status_getcoin = nhantien.get('mess', '')
                            print(nhantien)
                            xu_gained = 0
                            success = False
                            
                            if status_getcoin and "Thành công, bạn đã được cộng" in status_getcoin:
                                try:
                                    xu_gained = int(status_getcoin.split("Thành công, bạn đã được cộng ")[1].split(" xu")[0])
                                    self._log(f"│    ✅ {task_display}: +{xu_gained} xu")
                                    account_total_xu += xu_gained
                                    self.global_stats['xu_earned'] += xu_gained
                                    success = True
                                except Exception as parse_err:
                                    self._log(f"│    ⚠️  Parse xu lỗi: {str(parse_err)[:50]}")
                            elif status_getcoin:
                                # Only log if response is NOT empty
                                if status_getcoin.strip():
                                    self._log(f"│    ℹ️  {task_display}: {status_getcoin[:60]}")
                            
                            if success:
                                account_tasks_done += 1
                                self.global_stats['tasks_done'] += 1
                                
                                # Update tree with current progress
                                self._update_tree(ttc_user, f"⏳ {task_display} ({account_tasks_done}/{self.stop_after_tasks})", str(account_total_xu))
                                self._update_stats(
                                    tasks_done=self.global_stats['tasks_done'],
                                    xu_earned=self.global_stats['xu_earned'],
                                    tasks_error=self.global_stats['tasks_error']
                                )
                                
                                # Check task status after success (log delay + check limits)
                                should_break, reason = self.status_run(ttc_user, task['type_job'], account_total_xu)
                                if should_break:
                                    if reason == 'job_done':
                                        self._log(f"│    🎉 {task_display} đã đủ, chuyển task khác")
                                        # Check if all tasks have been completed
                                        if self._all_tasks_done():
                                            self._log(f"└─ ✅ Tất cả tasks hoàn thành, dừng acc {ttc_user}")
                                            self._update_tree(ttc_user, f"✅ Xong {account_total_xu}xu", str(account_total_xu))
                                            self._log(f"==================== END: {ttc_user} ====================")
                                            self._log(f"📊 Tổng kết: Done={account_tasks_done}, Xu={account_total_xu}, Error={account_tasks_error}\n")
                                            return
                                        break
                                    elif reason == 'run_done':
                                        self._log(f"└─ ✅ Đạt giới hạn, dừng acc {ttc_user}")
                                        self._update_tree(ttc_user, f"✅ Xong {account_total_xu}xu", str(account_total_xu))
                                        self._log(f"==================== END: {ttc_user} ====================")
                                        self._log(f"📊 Tổng kết: Done={account_tasks_done}, Xu={account_total_xu}, Error={account_tasks_error}\n")
                                        return
                            else:
                                self._log(f"│    ⚠️  {task_display}: Không thể parse phần thưởng")
                                time.sleep(5)
                        else:
                            self._log(f"│    ❌ {task_display}: Action block/lỗi")
                            account_tasks_error += 1
                            # Update status to show error
                            self._update_tree(ttc_user, f"❌ {task_display} block", str(account_total_xu))
                        
                        # Check if reached limit
                        if account_tasks_done >= self.stop_after_tasks:
                            self._log(f"└─ ✅ Đã tích lũy {self.stop_after_tasks} tasks")
                            self._update_tree(ttc_user, f"✅ Hoàn {account_total_xu}xu", str(account_total_xu))
                            self._log(f"==================== END: {ttc_user} ====================")
                            self._log(f"📊 Tổng kết: Done={account_tasks_done}, Xu={account_total_xu}, Error={account_tasks_error}\n")
                            return
                
                # After completing the task loop, check if all tasks are done
                if self._all_tasks_done():
                    self._log(f"└─ ✅ Tất cả tasks hoàn thành, dừng acc {ttc_user}")
                    self._update_tree(ttc_user, f"✅ Xong {account_total_xu}xu", str(account_total_xu))
                    self._log(f"==================== END: {ttc_user} ====================")
                    self._log(f"📊 Tổng kết: Done={account_tasks_done}, Xu={account_total_xu}, Error={account_tasks_error}\n")
                    return
                
        except Exception as e:
            self._log(f"❌ Exception: {str(e)}")
            self._update_tree(ttc_user, "❌ Exception", str(account_total_xu if 'account_total_xu' in locals() else 0))
            self.global_stats['tasks_error'] += 1
            self._update_stats(tasks_error=self.global_stats['tasks_error'])


    def main(self):
        for acc in self.data['accounts']:
            thread = threading.Thread(target=self.run_ttc, args=(acc,))
            thread.start()

# RUN_TTC({
#   "settings": {
#     "api_key": "f",
#     "delay_short": 5,
#     "delay_long": 60,
#     "delay_after_tasks": 5,
#     "stop_after_tasks": 100
#   },
#   "tasks": [
#     {
#       "type_job": "likepostvipcheo",
#       "display_name": "Like VIP",
#       "delay_min": 5,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "likepostvipre",
#       "display_name": "Like Thường",
#       "delay_min": 5,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "camxucvipcheo",
#       "display_name": "Cảm Xúc VIP",
#       "delay_min": 5,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "camxucvipre",
#       "display_name": "Cảm Xúc Thường",
#       "delay_min": 5,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "cmtcheo",
#       "display_name": "Bình Luận",
#       "delay_min": 8,
#       "delay_max": 120,
#       "count": 5
#     },
#     {
#       "type_job": "subcheo",
#       "display_name": "Theo Dõi",
#       "delay_min": 1,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "subcheofbvip",
#       "display_name": "Theo Dõi VIP",
#       "delay_min": 5,
#       "delay_max": 60,
#       "count": 1
#     },
#     {
#       "type_job": "sharecheo",
#       "display_name": "Share",
#       "delay_min": 10,
#       "delay_max": 120,
#       "count": 1
#     }
#   ],
#   "accounts": [
#     {
#       "ttc_user": "7sgBaPkSmQ",
#       "ttc_pass": "S5Ytk7rVb33v",
#       "ttc_token": "6dc18e6fe8c7dc314def77d99cc69c0d",
#       "fb_uid": "100002785140483",
#       "fb_cookie": "c_user=100002785140483; xs=15:qCAK7fDRlZ…",
#       "fb_proxy": "",
#       "fb_token": "EAAD6V7os0gcBRBfZBd2FswZAFkZCllAsoJFyzm1…"
#     }
#   ]
# }).main()