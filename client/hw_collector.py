import wmi
import psutil
import uuid
import math
import logging
import pythoncom
import ctypes

logging.basicConfig(filename='collector_error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mac_address():
    """获取物理网卡的MAC地址"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)]).upper()

def get_device_type(c):
    """获取设备类型: 笔记本/台式机"""
    try:
        system_enclosure = c.Win32_SystemEnclosure()[0]
        chassis_types = system_enclosure.ChassisTypes
        if chassis_types:
            type_code = chassis_types[0]
            # 8=Portable, 9=Laptop, 10=Notebook, 11=HandHeld, 14=Sub Notebook, 30=Tablet
            if type_code in [8, 9, 10, 11, 14, 30]:
                return "笔记本"
            # 3=Desktop, 4=Low Profile Desktop, 6=Mini Tower, 7=Tower
            elif type_code in [3, 4, 5, 6, 7, 13, 15, 16]:
                return "台式机"
            else:
                return "其他类型"
    except Exception as e:
        logging.error(f"获取设备类型失败: {e}")
    return "未知"

def get_brand_model(c):
    """获取品牌型号"""
    try:
        system = c.Win32_ComputerSystem()[0]
        manufacturer = system.Manufacturer.strip()
        model = system.Model.strip()
        return f"{manufacturer} {model}"
    except Exception as e:
        logging.error(f"获取品牌型号失败: {e}")
    return "未知"

def get_cpu_info(c):
    """获取CPU信息"""
    try:
        cpu = c.Win32_Processor()[0]
        return cpu.Name.strip()
    except Exception as e:
        logging.error(f"获取CPU信息失败: {e}")
    return "未知"

def get_ram_size():
    """获取内存大小(GB)"""
    try:
        total_memory = psutil.virtual_memory().total
        # 转换为GB并向上取整
        return str(math.ceil(total_memory / (1024 ** 3)))
    except Exception as e:
        logging.error(f"获取内存失败: {e}")
    return "0"

def get_disk_size():
    """获取硬盘总大小(GB)"""
    try:
        total_disk = 0
        for partition in psutil.disk_partitions(all=False):
            if 'cdrom' in partition.opts or partition.fstype == '':
                continue
            usage = psutil.disk_usage(partition.mountpoint)
            total_disk += usage.total
        return str(math.ceil(total_disk / (1024 ** 3)))
    except Exception as e:
        logging.error(f"获取硬盘失败: {e}")
    return "0"

def get_screen_size(c):
    """获取屏幕尺寸(英寸)估算值"""
    # 尝试方法1: 通过 WMI 获取
    try:
        monitors = c.WmiMonitorBasicDisplayParams()
        if monitors:
            for m in monitors:
                width_cm = m.MaxActiveDisplayLogicalWidth
                height_cm = m.MaxActiveDisplayLogicalHeight
                if width_cm and height_cm:
                    diagonal_cm = math.sqrt(width_cm**2 + height_cm**2)
                    inches = diagonal_cm / 2.54
                    return f"{round(inches, 1)}"
    except Exception as e:
        logging.warning(f"无法通过WMI获取屏幕尺寸: {e}")

    # 尝试方法2: 通过 Windows API (GetDeviceCaps) 获取物理尺寸
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        
        # 为了获取真实的物理尺寸，需要设置 DPI 感知
        # 注意: 避免在这里调用 user32.SetProcessDPIAware()，否则会导致 Tkinter 窗口突然变小。
        # DPI 感知已在 main.py 启动时统一设置。
        
        hdc = user32.GetDC(0)
        # HORZSIZE (4) = 物理宽度(毫米), VERTSIZE (6) = 物理高度(毫米)
        width_mm = gdi32.GetDeviceCaps(hdc, 4)
        height_mm = gdi32.GetDeviceCaps(hdc, 6)
        user32.ReleaseDC(0, hdc)
        
        if width_mm and height_mm:
            diagonal_mm = math.sqrt(width_mm**2 + height_mm**2)
            inches = diagonal_mm / 25.4
            return f"{round(inches, 1)}"
    except Exception as e:
        logging.warning(f"无法通过 Windows API 获取屏幕尺寸: {e}")
        
    return ""

def collect_all_info():
    """收集所有信息并返回字典"""
    pythoncom.CoInitialize()  # 必须在子线程初始化 COM
    logging.info("开始收集硬件信息...")
    info = {
        "mac_address": get_mac_address(),
        "device_type": "未知",
        "brand_model": "未知",
        "cpu_info": "未知",
        "ram_size": get_ram_size(),
        "disk_size": get_disk_size(),
        "screen_size": ""
    }
    
    try:
        c = wmi.WMI()
        info["device_type"] = get_device_type(c)
        info["brand_model"] = get_brand_model(c)
        info["cpu_info"] = get_cpu_info(c)
        
        try:
            # WmiMonitorBasicDisplayParams 在 wmi_root\wmi 命名空间下
            c_wmi = wmi.WMI(namespace="wmi")
            screen = get_screen_size(c_wmi)
            if screen:
                info["screen_size"] = screen
        except Exception as e:
            logging.warning(f"获取屏幕尺寸失败(命名空间wmi访问错误): {e}")

    except Exception as e:
        logging.error(f"初始化WMI失败: {e}")
    finally:
        pythoncom.CoUninitialize()

    logging.info("硬件信息收集完成。")
    return info

if __name__ == "__main__":
    print(collect_all_info())
