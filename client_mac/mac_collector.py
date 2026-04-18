import subprocess
import uuid
import math
import logging
import psutil
import re

logging.basicConfig(filename='collector_error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _run_cmd(cmd):
    """执行终端命令并返回输出字符串"""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        logging.error(f"Command failed: {cmd}, Error: {e}")
        return ""

def get_mac_address():
    """获取物理网卡 MAC 地址"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)]).upper()

def get_device_type(model_id):
    """根据型号判断设备类型"""
    if "MacBook" in model_id:
        return "笔记本"
    elif "iPad" in model_id or "iPhone" in model_id:
        return "移动设备"
    return "台式机"

def get_brand_model():
    """获取品牌和设备型号"""
    model_id = _run_cmd("sysctl -n hw.model")
    return "Apple", model_id

def get_cpu_info():
    """获取 CPU 品牌及型号"""
    return _run_cmd("sysctl -n machdep.cpu.brand_string")

def get_ram_size():
    """获取总内存大小 (GB)"""
    try:
        total = psutil.virtual_memory().total
        return str(math.ceil(total / (1024**3)))
    except Exception as e:
        logging.error(f"获取内存失败: {e}")
        return "0"

def get_disk_size():
    """获取系统盘总容量 (GB)"""
    try:
        total = psutil.disk_usage('/').total
        return str(math.ceil(total / (1024**3)))
    except Exception as e:
        logging.error(f"获取硬盘失败: {e}")
        return "0"

def get_screen_size():
    """获取屏幕物理尺寸 (英寸)"""
    output = _run_cmd("system_profiler SPDisplaysDataType")
    # 匹配 "13-inch", "16-inch", "13.3-inch" 等
    match = re.search(r"(\d+\.?\d*)-inch", output)
    if match:
        return match.group(1)
    return ""

def collect_all_info():
    """汇总所有硬件信息"""
    logging.info("开始采集 macOS 硬件信息...")
    brand, model_id = get_brand_model()
    info = {
        "mac_address": get_mac_address(),
        "device_type": get_device_type(model_id),
        "brand_model": f"{brand} {model_id}",
        "cpu_info": get_cpu_info(),
        "ram_size": get_ram_size(),
        "disk_size": get_disk_size(),
        "screen_size": get_screen_size()
    }
    logging.info("macOS 硬件信息采集完成。")
    return info

if __name__ == "__main__":
    print(collect_all_info())
