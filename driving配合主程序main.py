import base64
import urllib.parse
import requests
from PIL import Image, ImageTk
import re
import tkinter as tk
from tkinter import messagebox  # 需要导入 tk 组件

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

def handle_image_recognition(file_path, update_image_label, result_text):
    """
    处理图片识别的逻辑，包括图片预览和调用识别API
    """
    try:
        # 显示图片预览
        image = Image.open(file_path)
        image.thumbnail((300, 300))  # 限制图片最大尺寸为 300x300
        photo = ImageTk.PhotoImage(image)

        # 固定图片显示区域
        update_image_label(photo)

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
