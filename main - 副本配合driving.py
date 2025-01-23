import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD  # 用于拖放功能
from driving配合主程序main import handle_image_recognition  # 导入处理图片识别的函数
import pyperclip  # 用于复制到剪贴板

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
    handle_image_recognition(file_path, update_image_label, result_text)

def update_image_label(photo):
    """
    更新图片预览标签
    """
    image_label.config(image=photo, width=300, height=300)
    image_label.image = photo  # 保持对图像的引用

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

def on_file_drop(event):
    """
    处理拖放文件到窗口
    """
    file_path = event.data.strip()  # 获取拖放的文件路径
    if file_path:
        handle_image_recognition(file_path, update_image_label, result_text)

# 创建主窗口
root = TkinterDnD.Tk()
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
