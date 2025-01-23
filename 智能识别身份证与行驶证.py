# 1. 标准库模块
import os
import base64
import re
import urllib
import webbrowser
from functools import partial

# 2. 第三方库模块
import requests
import pyperclip
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

# 3. 自定义模块
from registration import check_config_file, check_password, show_generated_password  # 导入注册模块

# 4. UI 相关模块
import tkinter as tk  # tkinter 应该放在 UI 相关部分，作为主库导入



# 中心化窗口
def center_window(window, width=460, height=300):
    """Center a tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

# GUI for password checking
app = tk.Tk()
app.title("智能识别身份证与行驶证")
center_window(app, 460, 300)

label = tk.Label(app, text="输入注册码")
label.pack(pady=20)

password_entry = tk.Entry(app, width=30)
password_entry.pack(pady=10)

show_password_button = tk.Button(app, text="显示机器码", command=lambda: show_generated_password(app))
show_password_button.pack(pady=10)

# 抖音获取注册码
label_text = "关注抖音号：dubaishun12\n私信博主，免费获取注册码！"
label_font = ('Arial', 12, 'bold')  # 使用Arial字体，12号，粗体
label_foreground = "white"  # 文本颜色设置为白色
label_background = "orange"  # 背景颜色设置为红色

info_label = tk.Label(app, text=label_text, font=label_font, fg=label_foreground, bg=label_background)
info_label.pack(pady=20)

# 显示主窗体的方法
def show_main_window(app, root):
    app.destroy()  # 销毁注册窗口
    root.deiconify()  # 显示主窗体
    root.mainloop()  # 保持主窗口运行

# 注册窗口中的按钮
submit_button = tk.Button(
    app,
    text="提 交",
    command=lambda: check_password(password_entry, app, lambda: show_main_window(app, root))
)
submit_button.pack(pady=10)

API_KEY = "tOlHQ691Kpf8fuQUid9ZRjln"
SECRET_KEY = "OptXkNJ2C3IKUPzlVbkSxamr9ILqumiY"

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

        # 确保主窗口显示后再加载图像
        root.deiconify()  # 显示主窗口
        root.after(100, show_image, file_path)

def drag_and_drop(event):
    # 获取拖放的文件路径
    file_path = event.data

    # 去除路径中的大括号
    file_path = file_path.strip('{}')  # 去除大括号

    if file_path:
        # 调用识别函数
        result = recognize_image(file_path)
        if result:
            formatted_result = format_result(result)
            # 在显示结果时叠加之前的内容
            display_result(formatted_result, result_text)
            show_image(file_path)


def show_image(image_path):
    """
    显示图片在窗口的标签中，图片预览设置为 300x300，且不变形。
    :param image_path: 图片路径
    """
    # 加载图片
    img = Image.open(image_path)
    img.thumbnail((300, 300))  # 设置图片预览的最大尺寸为 300x300，保持比例

    # 将图像转换为 Tkinter 可用格式
    img_tk = ImageTk.PhotoImage(img)

    # 确保主窗口已经初始化
    if image_label.winfo_exists():
        image_label.config(image=img_tk, width=300, height=300)
        image_label.image = img_tk  # 保持对图像的引用
    else:
        print("Error: image_label not initialized correctly")

    
    # 创建标签并显示图像
    image_label.config(image=img_tk, width=300, height=300)
    image_label.image = img_tk  # 保持对图像的引用


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
    messagebox.showerror("识别失败", "非身份证和行驶证，不能识别！！")
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

        formatted_result = f"身份证信息：\n{name}\n{birth}\n{id_card_number}\n{address}"

    # 处理行驶证信息
    elif '车辆类型' in words_result:
        license_no = words_result.get("号牌号码", {}).get("words", "未识别")
        license_type = words_result.get("车辆类型", {}).get("words", "未识别")
        owner = words_result.get("所有人", {}).get("words", "未识别")
        brand = words_result.get("品牌型号", {}).get("words", "未识别")
        vehicle_identification_code = words_result.get("车辆识别代号", {}).get("words", "未识别")
        engine_no = words_result.get("发动机号码", {}).get("words", "未识别")
        issue_date = words_result.get("注册日期", {}).get("words", "未识别")
        valid_date = words_result.get("发证日期", {}).get("words", "未识别")
        

        # 格式化日期为 yyyy-MM-dd
        issue_date = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", issue_date)
        valid_date = re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", valid_date)

        formatted_result = f"行驶证信息：\n{license_no}\n{license_type}\n{owner}\n{brand}\n{vehicle_identification_code}\n{engine_no}\n{issue_date}\n{valid_date}"

    else:
        formatted_result = "未能识别身份证或行驶证"

    return formatted_result

def display_result(formatted_result, result_text):
    """
    显示格式化后的识别结果，并叠加显示之前的内容
    :param formatted_result: 格式化后的识别结果字符串
    :param result_text: 显示结果的文本框
    """
    # 获取当前文本框的内容
    current_text = result_text.get(1.0, tk.END).strip()
    
    # 如果当前文本框有内容，换行后追加新内容，添加两个换行符
    if current_text:
        formatted_result = "\n\n" + formatted_result
    
    # 在文本框中叠加显示识别结果
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
        #messagebox.showinfo("复制成功", "识别内容已复制到剪贴板！")
        # 清空文本框内容
        result_text.delete(1.0, tk.END)
    else:
        messagebox.showwarning("警告", "文本框为空，无法复制！")

def clear_text():
    """
    清空文本框内容
    """
    result_text.delete(1.0, tk.END)

def open_link():
    """
    打开速光网络软件开发的链接
    """
    webbrowser.open("https://www.douyin.com/user/MS4wLjABAAAAqiYlKxHAlPI_QzUANR22KZbclBuzbHruD0tqZH5EsoE?from_tab_name=main")

# 创建主窗口
root = TkinterDnD.Tk()  # 使用 TkinterDnD.Tk() 代替 tk.Tk()
root.title("智能识别身份证与行驶证")
window_width = 755
window_height = 500
center_window(root, window_width, window_height)

# 左侧图片显示区域
image_label = tk.Label(root, text="图片预览，支持拖放", width=50, height=18, relief="solid", anchor="center", bg="lightgray")
image_label.grid(row=0, column=0, rowspan=1, padx=10, pady=24, sticky="nsew")

# 绑定拖拽事件
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drag_and_drop)

# 左侧按钮
recognize_button = tk.Button(root, text="上传图片并识别", command=select_and_recognize_image, width=20)
recognize_button.grid(row=2, column=0, padx=10, pady=10)

# 右侧按钮和文本显示区
copy_button = tk.Button(root, text="剪  切", command=copy_to_clipboard, width=15, bg="#87cefa")
copy_button.grid(row=2, column=1, padx=10, pady=5)

clear_button = tk.Button(root, text="清  空", command=clear_text, width=15, bg="#87cefa")
clear_button.grid(row=3, column=1, padx=10, pady=5)

# 右侧文本显示区域
result_text = tk.Text(root, wrap=tk.WORD, height=24, width=50)
result_text.grid(row=0, column=1, rowspan=2, padx=10, pady=24, sticky="nsew")

# 让左侧和右侧列都固定
root.grid_rowconfigure(0, weight=1)  # 让行0的高度固定
root.grid_columnconfigure(0, weight=1)  # 让列0的宽度固定
root.grid_columnconfigure(1, weight=1)  # 让列1的宽度固定

# 底部链接
footer_label = tk.Label(root, text="软件作者：速光网络软件开发", fg="blue", bg="orange",  cursor="hand2", font=("Arial", 12, "bold", "underline"))
footer_label.grid(row=4, column=0, columnspan=2, pady=20)
footer_label.bind("<Button-1>", lambda e: open_link())


# 隐藏主程序窗口
#root.withdraw()
root.deiconify()
# 开始执行密码检查程序
if check_config_file():  # 密码检查成功
    app.destroy()  # 销毁注册窗口
    root.deiconify()  # 显示主程序窗口
    root.mainloop()  # 启动主窗口事件循环
else:
    app.mainloop()  # 保持注册窗口运行




 