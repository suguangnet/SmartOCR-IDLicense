import base64
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pyperclip
import re
import urllib
import os

API_KEY = "YLOtSqjT6U6rZOmCUk466hDg"
SECRET_KEY = "ukICHsUhKDyoZ34neD06k4XwISKnV5TL"

def center_window(window, width, height):
    """
    窗口居中显示
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def select_and_recognize_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return  # 如果用户未选择文件，直接返回
    
    # 调用识别函数
    result = recognize_image(file_path)
    if result:
        formatted_result = format_result(result)
        display_result(formatted_result, result_text)

def recognize_image(image_path):
    """
    识别图片，并根据返回的结果判断是身份证还是行驶证。
    :param image_path: 图片路径
    :return: 返回识别结果（如果识别失败，返回 None）
    """
    access_token = get_access_token()
    if not access_token:
        messagebox.showerror("错误", "获取 Access Token 失败")
        return None

    # 尝试进行身份证识别
    idcard_result = recognize_idcard_image(image_path, access_token)
    print("身份证识别结果：", idcard_result)  # 调试信息
    if idcard_result and idcard_result.get("words_result"):
        print("识别为身份证")
        return idcard_result  # 返回身份证识别结果
    
    # 如果身份证识别失败，尝试识别为行驶证
    vehicle_license_result = recognize_vehicle_license_image(image_path, access_token)
    print("行驶证识别结果：", vehicle_license_result)  # 调试信息
    if vehicle_license_result and vehicle_license_result.get("words_result"):
        print("识别为行驶证")
        return vehicle_license_result  # 返回行驶证识别结果
    
    # 如果两种识别都失败，返回None
    messagebox.showerror("识别失败", "无法识别图片是身份证还是行驶证")
    return None

def recognize_idcard_image(image_path, access_token):
    """
    识别身份证图片
    :param image_path: 图片路径
    :param access_token: 百度 API 认证的 token
    :return: 身份证识别结果
    """
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/idcard?access_token={access_token}"
    payload = {
        'id_card_side': 'front',  # 识别身份证正面
        'detect_ps': False,
        'detect_risk': False,
        'detect_photo': False,
        'detect_card': False,
        'detect_direction': False
    }

    img_base64 = get_file_content_as_base64(image_path)
    data = {'image': img_base64, **payload}

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def recognize_vehicle_license_image(image_path, access_token):
    """
    识别行驶证图片
    :param image_path: 图片路径
    :param access_token: 百度 API 认证的 token
    :return: 行驶证识别结果
    """
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/vehicle_license?access_token={access_token}"
    image_base64 = get_file_content_as_base64(image_path, urlencoded=True)
    if not image_base64:
        return None

    payload = f"image={image_base64}&detect_direction=false&unified=false&quality_warn=false"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def format_result(result):
    """
    格式化识别结果
    :param result: 从 API 返回的识别结果
    :return: 格式化后的识别结果字符串
    """
    words_result = result.get("words_result", {})

    # 处理身份证信息
    if '姓名' in words_result:
        name = words_result.get("姓名", {}).get("words", "未识别")
        birth = words_result.get("出生", {}).get("words", "未识别")
        id_card_number = words_result.get("公民身份号码", {}).get("words", "未识别")
        address = words_result.get("住址", {}).get("words", "未识别")

        # 使用正则表达式确保出生日期格式为 yyyy/MM/dd
        birth = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1/\2/\3", birth)

        # 格式化身份证号码和地址，无需做更改
        id_card_number = re.sub(r"(\d{6})(\d{8})(\d{3})(\w{1})", r"\1\2\3\4", id_card_number)

        formatted_result = f"身份证\n{name}\n{birth}\n{id_card_number}\n{address}"

    # 处理行驶证信息
    elif '车辆类型' in words_result:
        license_type = words_result.get("车辆类型", {}).get("words", "未识别")
        license_no = words_result.get("号牌号码", {}).get("words", "未识别")
        owner = words_result.get("所有人", {}).get("words", "未识别")
        engine_no = words_result.get("发动机号码", {}).get("words", "未识别")
        vehicle_identification_code = words_result.get("车辆识别代号", {}).get("words", "未识别")
        issue_date = words_result.get("注册日期", {}).get("words", "未识别")
        valid_date = words_result.get("发证日期", {}).get("words", "未识别")
        brand = words_result.get("品牌型号", {}).get("words", "未识别")

        # 格式化日期为 yyyy-MM-dd
        issue_date = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", issue_date)
        valid_date = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", valid_date)

        # 拼接行驶证的完整结果
        formatted_result = f"{license_no}\n{license_type}\n{owner}\n{brand}\n{vehicle_identification_code}\n{engine_no}\n{issue_date}\n{valid_date}"

    else:
        formatted_result = "未能识别身份证或行驶证"

    return formatted_result





def display_result(formatted_result, result_text):
    """
    显示格式化后的识别结果
    :param formatted_result: 格式化后的识别结果字符串
    :param result_text: 显示结果的文本框
    """
    # 清空之前的内容
    result_text.delete(1.0, "end")
    
    # 显示格式化后的结果
    result_text.insert("end", formatted_result)

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def copy_to_clipboard():
    """
    复制文本框内容到剪贴板
    """
    content = result_text.get(1.0, tk.END).strip()
    if content:
        pyperclip.copy(content)
        messagebox.showinfo("复制成功", "识别内容已复制到剪贴板！")
    else:
        messagebox.showwarning("警告", "文本框为空，无法复制！")

def clear_text():
    """
    清空文本框内容
    """
    result_text.delete(1.0, tk.END)

# 创建主窗口
root = tk.Tk()
root.title("身份证与行驶证智能识别")
window_width = 700
window_height = 450
center_window(root, window_width, window_height)

# 左侧图片显示区域
image_label = tk.Label(root, text="图片预览", width=40, height=15, relief="solid", anchor="center", bg="lightgray")
image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

# 左侧按钮
recognize_button = tk.Button(root, text="选择图片并识别", command=select_and_recognize_image, width=20)
recognize_button.grid(row=3, column=0, padx=10, pady=10)

# 右侧按钮和文本显示区
copy_button = tk.Button(root, text="复制结果", command=copy_to_clipboard, width=15, bg="#87cefa")
copy_button.grid(row=2, column=1, padx=10, pady=5)

clear_button = tk.Button(root, text="清空", command=clear_text, width=15, bg="#87cefa")
clear_button.grid(row=3, column=1, padx=10, pady=5)

result_text = tk.Text(root, wrap=tk.WORD, height=20, width=40)
result_text.grid(row=0, column=1, rowspan=2, padx=10, pady=10)

root.mainloop()
