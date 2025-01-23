import base64
import urllib
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import re

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
    match = re.match(r"(\d{4})(\d{2})(\d{2})", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return date_str
