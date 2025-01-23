import base64
import urllib
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pyperclip
import re  # 导入正则表达式模块

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
    
    # 调用身份证识别并显示结果
    result = recognize_idcard(file_path)
    if result:
        formatted_result = format_result(result)
        display_result(formatted_result, result_text)

def recognize_idcard(image_path):
    """
    识别身份证图片的函数
    :param image_path: 图片路径
    :return: 识别结果的 JSON 格式，或 None（如果失败）
    """
    access_token = get_access_token()
    if not access_token:
        messagebox.showerror("错误", "获取 Access Token 失败")
        return None

    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/idcard?access_token={access_token}"
    payload = {
        'id_card_side': 'front',  # 默认识别身份证正面
        'detect_ps': False,
        'detect_risk': False,
        'detect_photo': False,
        'detect_card': False,
        'detect_direction': False
    }

    # 获取图片的Base64编码
    img_base64 = get_file_content_as_base64(image_path)
    data = {'image': img_base64, **payload}

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        print("百度API响应内容:", response.text)  # 打印 API 返回的内容
        if response.status_code == 200:
            result = response.json()
            if 'error_code' in result:
                messagebox.showerror("识别失败", f"错误代码: {result['error_code']}\n错误信息: {result['error_msg']}")
            else:
                return result
        else:
            messagebox.showerror("错误", "请求百度 API 失败")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def format_result(result):
    """
    格式化识别结果，并使用正则表达式对信息进行处理
    :param result: 从 API 返回的识别结果
    :return: 格式化后的识别结果字符串
    """
    words_result = result.get("words_result", {})
    
    # 获取各个字段的内容
    name = words_result.get("姓名", {}).get("words", "未识别")
    birth = words_result.get("出生", {}).get("words", "未识别")
    id_card_number = words_result.get("公民身份号码", {}).get("words", "未识别")
    address = words_result.get("住址", {}).get("words", "未识别")

    # 使用正则表达式确保出生日期格式为 yyyy/MM/dd
    birth = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1/\2/\3", birth)

    # 格式化身份证号码和地址，无需做更改
    id_card_number = re.sub(r"(\d{6})(\d{8})(\d{3})(\w{1})", r"\1\2\3\4", id_card_number)

    # 拼接最终结果字符串
    formatted_result = f"{name}\n{birth}\n{id_card_number}\n{address}"

    return formatted_result


def display_result(formatted_result, result_text):
    """
    显示格式化后的身份证识别结果
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

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

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
root.title("身份证智能识别")
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

# 运行主循环
root.mainloop()
