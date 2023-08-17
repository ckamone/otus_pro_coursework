import functools
import logging
import socket
from optparse import OptionParser

from trex_stf_lib.trex_client import CTRexClient
from trex.astf.trex_astf_client import ASTFClient 
from trex.stl.trex_stl_client import STLClient


TREX_INSTANCES = [
    {'trex_ip': '127.0.0.1', 'master_daemon': '8091', 'daemon_ports': '8090', 
     'trex_sync_port': '4505', 'trex_async_port': '4504', 'mode': 'stl',
     'cfg': '/home/user/coursework/config_trex.yaml'},
]

def cases(cases):
    """Декоратор для запуска тесткейса с несколькими параметрами"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    logging.info(f'[{func.__name__}] start')
                    logging.info(f'[{func.__name__}] {new_args}')
                    func(*new_args)
                    logging.info(f'[{func.__name__}] done')
                except AssertionError:
                    raise AssertionError(f'{new_args}')

        return wrapper

    return decorator
                

class ServerManager:
    def __init__(self):
        self.master_clients = []

    @cases(TREX_INSTANCES)
    def check_connection_to_trex(self, trex_info):
        # logging.info(trex_info)
        try:
            socket.gethostbyaddr(trex_info['trex_ip'])
            # return True
        except socket.herror:
            logging.info("Unknown host")

    @cases(TREX_INSTANCES)
    def set_master_client(self, trex_info):
        # logging.info(trex_info)
        client = CTRexClient(
            trex_info['trex_ip'],
            master_daemon_port=trex_info['master_daemon'],
            trex_daemon_port=trex_info['daemon_ports'],
            trex_zmq_port=trex_info['trex_sync_port']
        )
        self.master_clients.append(client)


class TestManager:
    CLIENTS = []
    def __init__(self):
        self.client_class = None
        
    @classmethod
    @cases(TREX_INSTANCES)
    def set_base_client(cls, trex_info):
        client_class = STLClient if trex_info['mode'] == 'stl' else ASTFClient
        client = client_class(
            server=trex_info['trex_ip'],
            sync_port=trex_info['trex_sync_port'],
            async_port=trex_info['trex_async_port'],
        )
        cls.CLIENTS.append(client)

    # @classmethod
    # def add_client(cls, client):
    #     cls.CLIENTS.append(client)

    @cases(CLIENTS)
    def connect(self, trex_client):
        trex_client.connect()
        # logging.info(f'{trex_client.server} connect ok')


    @cases(CLIENTS)
    def disconnect(self, trex_client):
        trex_client.disconnect()
        # logging.info(f'{trex_client.server} disconnect ok')



# class ASTFTestManager(TestManager):
#     def __init__(self):
#         self.client_class = ASTFClient

# class STLTestManager(TestManager):
#     def __init__(self):
#         self.client_class = STLClient

if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-l", "--logfile", action="store", default=None)
    op.add_option("-m", "--mode", action="store", default='stl')
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.logfile, level=logging.INFO)

    # run trex
    trex_mng = ServerManager()
    trex_mng.check_connection_to_trex()
    trex_mng.set_master_client()
    for count, client in enumerate(trex_mng.master_clients):
        client.restart_trex_daemon()
        client.kill_all_trexes()
        if TREX_INSTANCES[count]['mode'] == 'stl':
            client.start_stateless(
                cfg=TREX_INSTANCES[count]['cfg'], iom=1)
        else:
            client.start_astf(
                cfg=TREX_INSTANCES[count]['cfg'], iom=1)

    # run test
    tst_mng = TestManager()
    tst_mng.set_base_client()
    # for client in TestManager.CLIENTS:
    #     client.connect()
    #     print('connected')
    #     client.disconnect()
    tst_mng.connect()
    tst_mng.disconnect()



# class Config:
#     def __init__(self):
#         self.server_ip = '172.17.118.179'
#         self.trex_count = 2
#         self.cores = ['1', '1']

#         self.master_daemon = ['8091', '8093']
#         self.daemon_ports = ['8090', '8092']
#         self.sync_ports = ['4505', '4508']
#         self.async_ports = ['4504', '4507']

#         self.profiles = ['/home/user/v3.02/scripts/research/realworld/real_realworld/sfr_1.py',
#                          '/home/user/v3.02/scripts/research/realworld/real_realworld/sfr_2.py']
#         self.cfg = ['/home/user/v3.02/scripts/research/realworld/real_realworld/config_trex.yaml',
#                     '/home/user/v3.02/scripts/research/realworld/real_realworld/config_trex2.yaml']

#         self.duration = 3
#         self.multiplier = 1 # munimum
#         self.step = 1 # step
#         self.maximum = 100 # (mbps)
#         self.allowed_diff = 50 # tx - rx (mbps)

#         # assert all((
#         #     len(self.sync_ports) == self.trex_count,
#         #     len(self.async_ports) == self.trex_count,
#         #     len(self.profiles) == self.trex_count,
#         #     len(self.cfg) == self.trex_count,
#         # ))


# class RealWorldTest():

#     def __init__(self, config_obj):
#         self.params = config_obj


#     def start_trex_astf(self, ip, mdport, tdport, tzport, cfg, cores):
#         print(ip, mdport, tdport, tzport, cfg, cores)
#         c = CTRexClient(
#             ip,
#             master_daemon_port=mdport,
#             trex_daemon_port=tdport,
#             trex_zmq_port=tzport
#         )
#         print('restart daemon')
#         c.restart_trex_daemon()
#         # print('kill trexes')
#         # c.kill_all_trexes()
#         print('starting trex')
#         c.start_astf(
#             cfg=cfg,
#             c=cores,  # 2
#             iom=1
#         )
#         print('done')
#         return c

#     def connect_trex_astf(self, server, sync_p, async_p):
#         c = ASTFClient(
#             server=server,
#             sync_port=sync_p,
#             async_port=async_p,
#         )
#         return c

#     def run(self, ):
#         try:
#             print('run trex_servers')
#             clients = []
#             clients_astf = []
#             for i in range(self.params.trex_count):
#                 print(i)
#                 c = self.start_trex_astf(
#                     ip=self.params.server_ip,
#                     mdport=int(self.params.master_daemon[i]),
#                     tdport=int(self.params.daemon_ports[i]),
#                     tzport=int(self.params.sync_ports[i]),
#                     cfg=self.params.cfg[i],
#                     cores=int(self.params.cores[i]),
#                 )
#                 clients.append(c)

#                 astf_c = self.connect_trex_astf(
#                     server=self.params.server_ip,
#                     sync_p=int(self.params.sync_ports[i]),
#                     async_p=int(self.params.async_ports[i])
#                 )
#                 print('connect')
#                 astf_c.connect()
#                 print('reset')
#                 astf_c.reset()
#                 astf_c.load_profile(self.params.profiles[i])
#                 clients_astf.append(astf_c)
#             if len(astf_c.get_active_ports())!=0:
#                 # start traffic
#                 for client in clients_astf:
#                     client.start(mult=self.params.multiplier)

#                 time.sleep(self.params.duration)
#                 actual_mult = self.params.step+self.params.multiplier
#                 while True:

#                     tx, rx = 0, 0
#                     for client in clients_astf:
#                         print('update')
#                         client.update(mult=actual_mult)
#                         stats = client.get_stats()
#                         tx += stats["total"]['tx_bps_L1'] / 1000000
#                         rx += stats["total"]['rx_bps_L1'] / 1000000

#                     print(f'TX (mbps) = {tx}, RX (mbps) = {rx}')
#                     actual_mult+=self.params.step
#                     if any((
#                         tx - rx > self.params.allowed_diff,
#                         tx >= self.params.maximum
#                     )):
#                         break
#                     time.sleep(self.params.duration)

#             for client in clients_astf:
#                 print('stop')
#                 client.stop()
#                 client.disconnect()

#         except Exception as e:
#             print(e)


# if __name__ == "__main__":
#     config = Config()

#     test = RealWorldTest(config)
#     test.run()