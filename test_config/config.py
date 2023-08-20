TREX_INSTANCES = [
    {'trex_ip': '127.0.0.1', 'master_daemon': '8091', 'daemon_ports': '8090', 
     'trex_sync_port': '4505', 'trex_async_port': '4504', 
     'cfg': '/home/user/coursework/trex_cfg/config_trex.yaml'},
    # {'trex_ip': '127.0.0.1', 'master_daemon': '8093', 'daemon_ports': '8092', 
    #  'trex_sync_port': '4509', 'trex_async_port': '4508',
    #  'cfg': '/home/user/coursework/trex_cfg/config_trex2.yaml'},
]

PROFILE = '/home/user/coursework/trex_traffic/udp_1pkt_simple.py'
SPEED_UNITS = 'mbps'
MIN_SPEED = 0.1
MAX_SPEED = 1
STEP = 0.1
DURATION = 3
UDP_PAYLOAD_SIZE = 10