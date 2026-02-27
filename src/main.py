import customtkinter as ctk
import subprocess
import os
import sys
import time
import threading
import json
import ctypes
import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
from tkinter import filedialog, messagebox

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class MirungApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.base_path = get_base_path()
        
        try:
            myappid = 'mirung.mirroring.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.title("미렁")
        self.geometry("400x520")
        self.resizable(False, False)

        try:
            self.iconbitmap(os.path.join(self.base_path, "icon.ico"))
        except Exception:
            pass
            
        self.process = None
        self.is_recording = False
        self.record_thread = None
        
        self.settings_file = os.path.join(self.base_path, "settings.json")
        self.screenshot_dir = os.path.expanduser("~\\Pictures")
        self.video_dir = os.path.expanduser("~\\Videos")
        self.load_settings()

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=ctk.X, padx=20, pady=(25, 0))

        self.settings_btn = ctk.CTkButton(self.header_frame, text="⚙", font=("맑은 고딕", 20), width=40, height=40, corner_radius=20, fg_color="transparent", hover_color="#333", text_color="white", command=self.open_settings)
        self.settings_btn.pack(side="left")

        self.title_label = ctk.CTkLabel(self.header_frame, text="미렁", font=("맑은 고딕", 36, "bold"), text_color="white")
        self.title_label.pack(side="left", padx=(10, 0))

        self.status_label = ctk.CTkLabel(self, text="준비됨", font=("맑은 고딕", 12), text_color="#AAAAAA")
        self.status_label.pack(pady=(10, 20))

        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.control_frame, text="미러링 시작", font=("맑은 고딕", 15, "bold"), width=320, height=60, corner_radius=30, fg_color="#27AE60", hover_color="#1E8449", command=self.start_mirror)
        self.start_btn.pack(pady=10)

        self.stop_btn = ctk.CTkButton(self.control_frame, text="미러링 중지", font=("맑은 고딕", 15, "bold"), width=320, height=60, corner_radius=30, fg_color="#E74C3C", hover_color="#C0392B", command=self.stop_mirror)
        self.stop_btn.pack(pady=10)
        
        self.capture_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.capture_frame.pack(pady=(20, 0))
        
        self.screenshot_btn = ctk.CTkButton(self.capture_frame, text="스크린샷", font=("맑은 고딕", 12), width=150, height=40, corner_radius=20, fg_color="#34495E", hover_color="#2C3E50", command=self.take_screenshot)
        self.screenshot_btn.pack(side="left", padx=10)
        
        self.record_btn = ctk.CTkButton(self.capture_frame, text="녹화 시작", font=("맑은 고딕", 12), width=150, height=40, corner_radius=20, fg_color="#E67E22", hover_color="#D35400", command=self.toggle_record)
        self.record_btn.pack(side="right", padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.screenshot_dir = data.get("screenshot_dir", self.screenshot_dir)
                    self.video_dir = data.get("video_dir", self.video_dir)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        data = {
            "screenshot_dir": self.screenshot_dir,
            "video_dir": self.video_dir
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_status(self, text, color="#AAAAAA"):
        self.status_label.configure(text=text, text_color=color)

    def open_settings(self):
        """저장 경로를 설정하는 새 창을 엽니다."""
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("저장 경로 설정")
        settings_win.geometry("400x200")
        settings_win.resizable(False, False)
        settings_win.attributes("-topmost", True)
        
        ctk.CTkLabel(settings_win, text="스크린샷 저장 위치:", font=("맑은 고딕", 12)).pack(pady=(20, 0))
        shot_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        shot_frame.pack(pady=5, fill=ctk.X)
        
        shot_lbl_scroll = ctk.CTkScrollableFrame(shot_frame, height=20, corner_radius=5, fg_color="#222")
        shot_lbl_scroll.pack(side="left", fill=ctk.X, expand=True, padx=(20, 5))
        
        self.shot_lbl = ctk.CTkLabel(shot_lbl_scroll, text=self.screenshot_dir, font=("맑은 고딕", 10), text_color="#AAAAAA", anchor="w")
        self.shot_lbl.pack(side="left")
        
        def change_shot_dir():
            d = filedialog.askdirectory(initialdir=self.screenshot_dir, title="스크린샷 저장 폴더 선택")
            if d:
                self.screenshot_dir = d
                self.shot_lbl.configure(text=self.screenshot_dir)
                self.save_settings()
                
        ctk.CTkButton(shot_frame, text="변경", width=50, height=30, corner_radius=15, fg_color="#555", hover_color="#444", command=change_shot_dir).pack(side="right", padx=(5, 20))

        ctk.CTkLabel(settings_win, text="동영상 저장 위치:", font=("맑은 고딕", 12)).pack(pady=(10, 0))
        vid_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        vid_frame.pack(pady=5, fill=ctk.X)
        
        vid_lbl_scroll = ctk.CTkScrollableFrame(vid_frame, height=20, corner_radius=5, fg_color="#222")
        vid_lbl_scroll.pack(side="left", fill=ctk.X, expand=True, padx=(20, 5))
        
        self.vid_lbl = ctk.CTkLabel(vid_lbl_scroll, text=self.video_dir, font=("맑은 고딕", 10), text_color="#AAAAAA", anchor="w")
        self.vid_lbl.pack(side="left")
        
        def change_vid_dir():
            d = filedialog.askdirectory(initialdir=self.video_dir, title="동영상 저장 폴더 선택")
            if d:
                self.video_dir = d
                self.vid_lbl.configure(text=self.video_dir)
                self.save_settings()
                
        ctk.CTkButton(vid_frame, text="변경", width=50, height=30, corner_radius=15, fg_color="#555", hover_color="#444", command=change_vid_dir).pack(side="right", padx=(5, 20))

    def rename_window_task(self):
        while self.process is not None:
            windows = gw.getWindowsWithTitle("Direct3D11 renderer")
            if not windows:
                windows = gw.getWindowsWithTitle("OpenGL renderer")
            if not windows:
                windows = gw.getWindowsWithTitle("Direct3D9 renderer")
            if not windows:
                windows = gw.getWindowsWithTitle("UxPlay")
            
            if windows:
                for win in windows:
                    hwnd = win._hWnd
                    ctypes.windll.user32.SetWindowTextW(hwnd, "미렁 화면")
                break
            time.sleep(0.5)

    def kill_zombie_uxplay(self):
        try:
            os.system("taskkill /f /im uxplay.exe >nul 2>&1")
        except Exception:
            pass

    def start_mirror(self):
        if self.process is None:
            self.kill_zombie_uxplay()
            
            uxplay_path = os.path.join(self.base_path, "uxplay_win", "uxplay.exe")
            
            home_dir = os.path.expanduser("~")
            rc_path = os.path.join(home_dir, ".uxplayrc")
            if os.path.exists(rc_path):
                try:
                    os.remove(rc_path)
                except Exception:
                    pass
            
            if os.path.exists(uxplay_path):
                try:
                    self.process = subprocess.Popen([uxplay_path, "-fps", "60"])
                    
                    threading.Thread(target=self.rename_window_task, daemon=True).start()
                    
                    self.update_status("미러링 중...", "#27AE60")
                    self.start_btn.configure(state="disabled")
                    self.record_btn.configure(state="normal")
                    self.screenshot_btn.configure(state="normal")
                except Exception as e:
                    messagebox.showerror("오류", f"미러링 수신기를 실행하지 못했습니다: {e}")
                    self.update_status("오류 발생", "#E74C3C")
                    self.kill_zombie_uxplay()
                    self.process = None
            else:
                messagebox.showerror("오류", f"uxplay.exe를 찾을 수 없습니다.\n확인된 경로: {uxplay_path}")
                self.update_status("설치 오류", "#E74C3C")

    def stop_mirror(self):
        if self.process:
            if self.is_recording:
                self.toggle_record()
            try:
                self.process.terminate()
                self.process.wait()
            except Exception:
                pass
            
            self.process = None
            
        self.kill_zombie_uxplay()
        self.update_status("Idle", "#AAAAAA")
        self.start_btn.configure(state="normal")
        self.record_btn.configure(state="disabled")
        self.screenshot_btn.configure(state="disabled")

    def take_screenshot(self):
        windows = gw.getWindowsWithTitle("미렁 화면")
        if windows:
            win = windows[0]
            if win.width > 0 and win.height > 0:
                bbox = (win.left, win.top, win.right, win.bottom)
                try:
                    img = ImageGrab.grab(bbox)
                    
                    if not os.path.exists(self.screenshot_dir):
                        try:
                            os.makedirs(self.screenshot_dir, exist_ok=True)
                        except Exception as e:
                            messagebox.showerror("오류", f"스크린샷 저장 폴더를 만들 수 없습니다: {e}")
                            return

                    filename = os.path.join(self.screenshot_dir, f"screenshot_{int(time.time())}.png")
                    img.save(filename)
                    print(f"Screenshot saved to: {filename}")
                except Exception as e:
                    messagebox.showerror("오류", f"스크린샷을 저장하지 못했습니다: {e}")
        else:
            messagebox.showwarning("경고", "캡처할 '미렁 화면' 창을 찾을 수 없습니다. 아이패드가 연결되어 있는지 확인해주세요.")

    def toggle_record(self):
        if not self.is_recording:
            windows = gw.getWindowsWithTitle("미렁 화면")
            if not windows:
                messagebox.showwarning("경고", "녹화할 '미렁 화면' 창을 찾을 수 없습니다.")
                return
                
            self.is_recording = True
            self.record_btn.configure(text="녹화 중지", fg_color="#C0392B", hover_color="#E74C3C")
            self.update_status("녹화 중...", "#E67E22")
            
            if not os.path.exists(self.video_dir):
                try:
                    os.makedirs(self.video_dir, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("오류", f"동영상 저장 폴더를 만들 수 없습니다: {e}")
                    return
            
            filename = os.path.join(self.video_dir, f"record_{int(time.time())}.mp4")
            self.record_thread = threading.Thread(target=self.record_task, args=(filename,), daemon=True)
            self.record_thread.start()
        else:
            self.is_recording = False
            self.record_btn.configure(text="녹화 시작", fg_color="#E67E22", hover_color="#D35400")
            
            if self.process:
                self.update_status("미러링 중...", "#27AE60")
            else:
                self.update_status("Idle", "#AAAAAA")

    def record_task(self, filename):
        windows = gw.getWindowsWithTitle("미렁 화면")
        if not windows:
            self.toggle_record()
            return
        
        win = windows[0]
        width, height = win.width, win.height
        
        if width == 0 or height == 0:
            print("Video dimension is 0. Cancel recording.")
            self.toggle_record()
            return
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        try:
            out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            if not out.isOpened():
                print("Could not open VideoWriter. Cancel recording.")
                self.toggle_record()
                return
        except Exception as e:
            print(f"Error creating VideoWriter: {e}")
            self.toggle_record()
            return
            
        while self.is_recording:
            windows = gw.getWindowsWithTitle("미렁 화면")
            if windows:
                win = windows[0]
                if win.width > 0 and win.height > 0:
                    bbox = (win.left, win.top, win.right, win.bottom)
                    try:
                        img = ImageGrab.grab(bbox)
                        frame = np.array(img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        frame_resized = cv2.resize(frame, (width, height))
                        
                        out.write(frame_resized)
                    except Exception as e:
                        print(f"Error grabbing frame: {e}")
                        break

            time.sleep(0.05)
            
        out.release()
        print(f"Recording saved to: {filename}")

    def on_closing(self):
        self.stop_mirror()
        self.kill_zombie_uxplay()
        self.destroy()

if __name__ == "__main__":
    app = MirungApp()
    app.update_status("Idle", "#AAAAAA")
    app.start_btn.configure(state="normal")
    app.record_btn.configure(state="disabled")
    app.screenshot_btn.configure(state="disabled")
    app.mainloop()