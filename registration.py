#registration.py
import configparser  #检查config.ini
import psutil
import hashlib
from tkinter import messagebox
def get_ipv4_mac():
    """Get the MAC address of the primary network interface"""
    for nic, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    return None

def mac_to_zcm(mac):
    """Convert MAC address to a custom registration code."""
    if not mac:
        return None

    m = hashlib.md5()
    m.update(mac.encode())
    m_md5 = m.hexdigest()

    zcm = [ord(i) if i.isalpha() else int(i) for i in m_md5]
    zcm_end = [str(i + 8) for i in zcm]
    
    return "".join(zcm_end)

def check_config_file():
    """Check if the registration code in config.ini matches the current machine."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'REGISTRATION' in config and 'code' in config['REGISTRATION']:
        stored_code = config['REGISTRATION']['code']
        current_code = mac_to_zcm(get_ipv4_mac())
        if stored_code == current_code:
            return True
    return False

def is_user_registered():
    """Check if the user is registered by reading config.ini"""
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        return False
    config.read('config.ini')
    return config.getboolean('DEFAULT', 'registered', fallback=False)

def check_password(password_entry, app, start_image_processor):
    """Check if the entered password matches the generated registration code."""
    try:
        entered_password = password_entry.get()
        generated_password = mac_to_zcm(get_ipv4_mac())
        if entered_password == generated_password:
            # Save the registration code to config.ini
            config = configparser.ConfigParser()
            config['REGISTRATION'] = {'code': generated_password}
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
            
            messagebox.showinfo("Success", "注册成功！")
            app.after(1000, start_image_processor)
        else:
            messagebox.showerror("Error", "注册码错误!")
    except Exception as e:
        messagebox.showerror("Error", f"Error checking password: {str(e)}")

def copy_mac_to_clipboard(app):
    """Copy MAC address to clipboard."""
    app.clipboard_clear()  # 清除剪贴板内容
    app.clipboard_append(get_ipv4_mac())  # 添加MAC地址到剪贴板
    app.update()  # 更新窗口内容
    messagebox.showinfo("Info", "机器码已复制到剪贴板！")

def show_generated_password(app):
    """Display the current machine's MAC."""
    try:
        current_mac = get_ipv4_mac()
        result = messagebox.askquestion("机器码", f"机器码为: {current_mac}\n\n是否复制机器码到剪贴板?", icon='info')
        if result == 'yes':
            copy_mac_to_clipboard(app)
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching MAC: {str(e)}")
