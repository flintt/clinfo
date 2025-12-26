# gunicorn.conf.py
import multiprocessing
import time
import socket
import logging
import traceback
from zeroconf import ServiceInfo, Zeroconf

# 定义一个独立的函数，用来在单独的进程中运行
def run_mdns_process(port):
    """
    这个函数会在一个干净的进程中运行，
    不受 Gunicorn/Eventlet 的 monkey_patch 影响。
    """
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("mdns-process")
    
    try:
        # 获取本机 IP (你的原始逻辑)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()

        logger.info(f"Starting mDNS broadcast for {local_ip}:{port}")

        # 准备服务信息
        info = ServiceInfo(
            type_="_http._tcp.local.",
            name="SocketIO Latency Tester._http._tcp.local.",
            addresses=[socket.inet_aton(local_ip)], # 确保转为二进制
            port=port,
            properties={'version': '1.0'},
            server="socketio-tester.local."
        )

        zc = Zeroconf()
        zc.register_service(info, allow_name_change=True)
        logger.info("mDNS Registered successfully. Keeping process alive.")

        # 死循环保持进程存活 (这是标准的多进程守护写法)
        while True:
            time.sleep(5)
            
    except Exception as e:
        logger.error(f"mDNS Process crashed: {e}")
        logger.error(traceback.format_exc())
    finally:
        # 进程退出前的清理
        if 'zc' in locals():
            zc.unregister_service(info)
            zc.close()

# 全局变量保存进程引用
mdns_process = None

def on_starting(server):
    """Gunicorn 主进程启动时执行"""
    global mdns_process
    
    # 这里的端口要和你启动命令一致
    target_port = 15001 
    
    print("Master process starting. Spawning mDNS subprocess...")
    
    # 启动一个标准的系统进程 (Process)，而不是线程
    mdns_process = multiprocessing.Process(target=run_mdns_process, args=(target_port,))
    mdns_process.daemon = True # 设置为守护进程，主进程死它也死
    mdns_process.start()

def on_exit(server):
    """Gunicorn 主进程退出时执行"""
    global mdns_process
    if mdns_process and mdns_process.is_alive():
        print("Master exiting. Terminating mDNS subprocess...")
        mdns_process.terminate()
        mdns_process.join()
