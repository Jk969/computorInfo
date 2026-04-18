import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import logging
from mac_collector import collect_all_info

logging.basicConfig(filename='collector_error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_URL = "http://47.109.135.123:36867/api/report"
# For local testing, you can change this to:
# SERVER_URL = "http://localhost:36867/api/report"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("电脑信息采集工具 (Mac版)")
        self.geometry("650x850")
        self.resizable(False, False)
        
        # 统一设置字体
        self.font_normal = ("Microsoft YaHei", 11)
        self.font_bold = ("Microsoft YaHei", 12, "bold")
        
        self.hw_info = {}
        
        self.create_widgets()
        self.load_hardware_info()

    def create_widgets(self):
        """创建界面元素"""
        padding_options = {'padx': 15, 'pady': 10}

        # 标题
        lbl_title = tk.Label(self, text="请核对以下硬件信息并补全必填项", font=("Microsoft YaHei", 14, "bold"))
        lbl_title.pack(pady=20)

        # 硬件信息展示区域 (只读)
        frame_hw = tk.LabelFrame(self, text="系统检测到的硬件信息", font=self.font_bold)
        frame_hw.pack(fill="x", padx=20, pady=10)

        self.lbl_mac = self.add_info_row(frame_hw, "MAC地址:", 0)
        self.lbl_type = self.add_info_row(frame_hw, "设备类型:", 1)
        self.lbl_brand = self.add_info_row(frame_hw, "品牌型号:", 2)
        self.lbl_cpu = self.add_info_row(frame_hw, "CPU信息:", 3)
        self.lbl_ram = self.add_info_row(frame_hw, "内存(GB):", 4)
        self.lbl_disk = self.add_info_row(frame_hw, "硬盘(GB):", 5)
        
        # 屏幕尺寸允许用户修改(因为检测可能不准)
        tk.Label(frame_hw, text="屏幕(英寸):", font=self.font_normal).grid(row=6, column=0, sticky="e", **padding_options)
        self.entry_screen = tk.Entry(frame_hw, width=30, font=self.font_normal)
        self.entry_screen.grid(row=6, column=1, sticky="w", **padding_options)

        # 用户填报区域
        frame_user = tk.LabelFrame(self, text="需补充的信息 (必填)", font=self.font_bold)
        frame_user.pack(fill="x", padx=20, pady=20)

        tk.Label(frame_user, text="采购年份:", font=self.font_normal).grid(row=0, column=0, sticky="e", **padding_options)
        
        # 为了增大下拉框字体，配置 ttk 样式
        style = ttk.Style()
        style.configure('TCombobox', font=self.font_normal)
        
        # 第一项设为空提示
        year_values = ["-- 请选择 --"] + [str(y) for y in range(2016, 2027)]
        self.combo_year = ttk.Combobox(frame_user, values=year_values, state="readonly", width=28, font=self.font_normal)
        self.combo_year.grid(row=0, column=1, sticky="w", **padding_options)
        self.combo_year.current(0)  # 默认选中第一项 "-- 请选择 --"

        tk.Label(frame_user, text="使用人:", font=self.font_normal).grid(row=1, column=0, sticky="e", **padding_options)
        self.entry_user = tk.Entry(frame_user, width=30, font=self.font_normal)
        self.entry_user.grid(row=1, column=1, sticky="w", **padding_options)

        # 提交按钮 (Mac 下的按钮不支持背景色，所以去除了 bg 和 fg)
        self.btn_submit = tk.Button(self, text="提 交 信 息", font=("Microsoft YaHei", 14, "bold"), command=self.submit_data)
        self.btn_submit.pack(pady=30, ipadx=40, ipady=10)

        self.lbl_status = tk.Label(self, text="", fg="gray", font=self.font_normal)
        self.lbl_status.pack()

    def add_info_row(self, parent, label_text, row_idx):
        """辅助方法: 添加一行只读信息展示"""
        tk.Label(parent, text=label_text, font=self.font_normal).grid(row=row_idx, column=0, sticky="e", padx=15, pady=8)
        lbl_val = tk.Label(parent, text="获取中...", fg="blue", font=self.font_normal)
        lbl_val.grid(row=row_idx, column=1, sticky="w", padx=15, pady=8)
        return lbl_val

    def load_hardware_info(self):
        """后台线程加载硬件信息，避免阻塞UI"""
        def task():
            self.hw_info = collect_all_info()
            # 在主线程更新UI
            self.after(0, self.update_hw_ui)
        threading.Thread(target=task, daemon=True).start()

    def update_hw_ui(self):
        """将获取到的硬件信息更新到界面"""
        self.lbl_mac.config(text=self.hw_info.get("mac_address", ""))
        self.lbl_type.config(text=self.hw_info.get("device_type", ""))
        self.lbl_brand.config(text=self.hw_info.get("brand_model", ""))
        
        cpu_text = self.hw_info.get("cpu_info", "")
        # 如果CPU名字太长，截断一下
        if len(cpu_text) > 30:
            cpu_text = cpu_text[:27] + "..."
        self.lbl_cpu.config(text=cpu_text)
        
        self.lbl_ram.config(text=self.hw_info.get("ram_size", ""))
        self.lbl_disk.config(text=self.hw_info.get("disk_size", ""))
        
        # 屏幕尺寸填入输入框
        self.entry_screen.delete(0, tk.END)
        self.entry_screen.insert(0, self.hw_info.get("screen_size", ""))

    def submit_data(self):
        """提交数据到服务端"""
        user_name = self.entry_user.get().strip()
        buy_year = self.combo_year.get().strip()
        screen_size = self.entry_screen.get().strip()

        if not user_name:
            messagebox.showwarning("提示", "请填写使用人！")
            return
        
        if not buy_year or buy_year == "-- 请选择 --":
            messagebox.showwarning("提示", "请选择采购年份！")
            return

        self.btn_submit.config(state="disabled", text="正在提交...")
        self.lbl_status.config(text="正在连接服务器...", fg="blue")

        payload = {
            "mac_address": self.hw_info.get("mac_address", ""),
            "device_type": self.hw_info.get("device_type", ""),
            "brand_model": self.hw_info.get("brand_model", ""),
            "cpu_info": self.hw_info.get("cpu_info", ""),
            "ram_size": self.hw_info.get("ram_size", ""),
            "disk_size": self.hw_info.get("disk_size", ""),
            "screen_size": screen_size,
            "buy_year": buy_year,
            "user_name": user_name
        }

        def post_task():
            try:
                response = requests.post(SERVER_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.after(0, self.on_submit_success)
                    else:
                        self.after(0, self.on_submit_fail, data.get("message", "服务器返回错误"))
                else:
                    self.after(0, self.on_submit_fail, f"HTTP错误: {response.status_code}")
            except Exception as e:
                logging.error(f"提交失败: {e}")
                self.after(0, self.on_submit_fail, f"网络请求异常: {str(e)}")

        threading.Thread(target=post_task, daemon=True).start()

    def on_submit_success(self):
        self.btn_submit.config(state="normal", text="提 交 信 息")
        self.lbl_status.config(text="提交成功！", fg="green")
        messagebox.showinfo("成功", "信息已成功提交！感谢您的配合。")
        self.destroy() # 提交成功后关闭程序

    def on_submit_fail(self, error_msg):
        self.btn_submit.config(state="normal", text="提 交 信 息")
        self.lbl_status.config(text="提交失败", fg="red")
        messagebox.showerror("提交失败", f"无法提交数据，请检查网络或联系管理员。\n错误信息: {error_msg}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
