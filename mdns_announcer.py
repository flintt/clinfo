import socket
from zeroconf import ServiceInfo, Zeroconf
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mdns_announcer")

def get_local_ip():
    """
    Determine the local IP address by connecting to a public DNS server.
    This does not actually send data.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def register_mdns_service(port, service_name="SocketIO Latency Tester"):
    """
    Register the service via mDNS.

    Args:
        port (int): The port the service is running on.
        service_name (str): The name of the service to broadcast.

    Returns:
        tuple: (zeroconf_instance, service_info)
    """
    local_ip = get_local_ip()
    try:
        # zeroconf expects IP address in bytes
        ip_bytes = socket.inet_aton(local_ip)
    except socket.error:
        logger.error(f"Could not convert IP {local_ip} to bytes.")
        return None, None

    # Service type for a web server
    desc = {'path': '/'}

    # Ensure the name is unique-ish or standard.
    # Format: instance_name._service_type._protocol.local.
    type_ = "_http._tcp.local."
    name = f"{service_name}.{type_}"

    logger.info(f"Registering mDNS service: {name} at {local_ip}:{port}")

    info = ServiceInfo(
        type_,
        name,
        addresses=[ip_bytes],
        port=port,
        properties=desc,
        server=f"{socket.gethostname()}.local.",
    )

    zeroconf = Zeroconf()
    try:
        zeroconf.register_service(info)
        logger.info("mDNS service registered successfully.")
        return zeroconf, info
    except Exception as e:
        logger.error(f"Failed to register mDNS service: {e}")
        zeroconf.close()
        return None, None

def unregister_mdns_service(zeroconf, info):
    """
    Unregister the mDNS service.

    Args:
        zeroconf (Zeroconf): The zeroconf instance.
        info (ServiceInfo): The service info.
    """
    if zeroconf and info:
        logger.info("Unregistering mDNS service...")
        try:
            zeroconf.unregister_service(info)
            zeroconf.close()
            logger.info("mDNS service unregistered.")
        except Exception as e:
            logger.error(f"Error unregistering mDNS service: {e}")
