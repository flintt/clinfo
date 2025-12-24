# gunicorn.conf.py
import atexit
from mdns_announcer import register_mdns_service, unregister_mdns_service

# 全局变量，用于保存 mdns 实例，防止被垃圾回收
mdns_instances = {}

def on_starting(server):
    """主进程启动时调用（可选，仅打印日志）"""
    print("Gunicorn master process starting...")

def post_worker_init(worker):
    """
    关键点：当 Worker 进程初始化完成后调用。
    在这里启动 mDNS，可以确保线程是在 Worker 进程内部创建的。
    """
    # 这里的 15001 要和你 Gunicorn 启动命令里的端口一致
    # 也可以通过解析 server.address 来动态获取，但写死最稳
    port = 15001 
    
    print(f"Worker {worker.pid} initialized. Registering mDNS on port {port}...")
    
    # 启动 mDNS
    zc, info = register_mdns_service(port=port)
    
    # 保存引用
    mdns_instances['zc'] = zc
    mdns_instances['info'] = info

def worker_exit(server, worker):
    """
    当 Worker 进程退出时调用。
    在这里注销 mDNS 服务。
    """
    print(f"Worker {worker.pid} exiting. Unregistering mDNS...")
    
    zc = mdns_instances.get('zc')
    info = mdns_instances.get('info')
    
    if zc and info:
        unregister_mdns_service(zc, info)
