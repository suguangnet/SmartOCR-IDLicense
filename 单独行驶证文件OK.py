import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD  # 用于拖放功能
import base64
import urllib.parse
import requests
from PIL import Image, ImageTk
import pyperclip  # 用于复制到剪贴板

API_KEY = "YLOtSqjT6U6rZOmCUk466hDg"
SECRET_KEY = "ukICHsUhKDyoZ34neD06k4XwISKnV5TL"

def get_file_content_as_base64(path, urlencoded=False):
    try:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            if urlencoded:
                content = urllib.parse.quote_plus(content)
        return content
    except FileNotFoundError:
        messagebox.showerror("错误", f"文件未找到: {path}")
        return None

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("错误", f"获取Access Token失败: {e}")
        return None

def recognize_vehicle_license(image_path):
    image_base64 = get_file_content_as_base64(image_path, urlencoded=True)
    if not image_base64:
        return None

    access_token = get_access_token()
    if not access_token:
        return None

    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/vehicle_license?access_token={access_token}"
    payload = f"image={image_base64}&detect_direction=false&unified=false&quality_warn=false"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("错误", f"HTTP请求失败: {e}")
        return None

def select_and_recognize_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return  # 如果用户未选择文件，直接返回
    handle_image_recognition(file_path)

import re  # 引入正则表达式模块

def format_date(date_str):
    """
    将日期格式从连续数字转换为 YYYY-MM-DD
    :param date_str: 连续数字日期 (如 20221020)
    :return: 格式化后的日期 (如 2022-10-20) 或原始字符串（如果格式不符合）
    """
    match = re.match(r"(\d{4})(\d{2})(\d{2})", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return date_str

def handle_image_recognition(file_path):
    """
    处理图片识别的逻辑，包括图片预览和调用识别API
    """
    try:
        # 显示图片预览
        image = Image.open(file_path)
        image.thumbnail((300, 300))  # 限制图片最大尺寸为 300x300
        photo = ImageTk.PhotoImage(image)

        # 固定图片显示区域
        image_label.config(image=photo, width=300, height=300)
        image_label.image = photo

        # 调用行驶证识别功能
        result = recognize_vehicle_license(file_path)
        if result and "words_result" in result:
            words_result = result["words_result"]
            required_fields = [
                "号牌号码", "车辆类型", "所有人", "品牌型号",
                "车辆识别代号", "发动机号码", "注册日期", "发证日期"
            ]
            
            result_text.delete(1.0, tk.END)  # 清空结果框
            for field in required_fields:
                value = words_result.get(field, {}).get("words", "未识别到")
                
                # 检查是否是日期字段并格式化
                if field in ["注册日期", "发证日期"]:
                    value = format_date(value)
                
                # 直接显示数据，而不包含字段名称
                result_text.insert(tk.END, f"{value}\n")
        else:
            messagebox.showerror("错误", "识别失败或无结果返回")
    except Exception as e:
        messagebox.showerror("错误", f"图片处理失败: {e}")



def copy_to_clipboard():
    """
    复制文本框内容到剪贴板
    """
    content = result_text.get(1.0, tk.END).strip()
    if content:
        pyperclip.copy(content)
        #messagebox.showinfo("复制成功", "识别内容已复制到剪贴板！")
    else:
        messagebox.showwarning("警告", "文本框为空，无法复制！")

def clear_text():
    """
    清空文本框内容
    """
    result_text.delete(1.0, tk.END)

def on_file_drop(event):
    """
    处理拖放文件到窗口
    """
    file_path = event.data.strip()  # 获取拖放的文件路径
    if file_path:
        handle_image_recognition(file_path)

def center_window(window, width, height):
    """
    窗口居中显示
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# 创建主窗口
root = TkinterDnD.Tk()  # 使用 TkinterDnD 提供拖放功能
root.title("身份证和行驶证智能识别")
window_width = 700
window_height = 450
center_window(root, window_width, window_height)  # 设置窗口居中

# 左侧图片显示区域
image_label = tk.Label(root, text="图片预览", width=40, height=15, relief="solid", anchor="center", bg="lightgray")
image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

# 左侧按钮
recognize_button = tk.Button(root, text="选择图片并识别", command=select_and_recognize_image, width=20)
recognize_button.grid(row=3, column=0, padx=10, pady=10)

# 右侧按钮和文本显示区

copy_button = tk.Button(root, text="复  制", command=copy_to_clipboard, width=15, bg="#87cefa")
copy_button.grid(row=2, column=1, padx=10, pady=5)

clear_button = tk.Button(root, text="清  空", command=clear_text, width=15, bg="#87cefa")
clear_button.grid(row=3, column=1, padx=10, pady=5)

result_text = tk.Text(root, wrap=tk.WORD, height=20, width=40)
result_text.grid(row=0, column=1, rowspan=2, padx=10, pady=10)


# 设置拖放图片
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_file_drop)

# 运行主循环
root.mainloop()
