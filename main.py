import functools
import logging
import time
from datetime import datetime
from parser.op_parser import get_args
from test_config.config import *

from trex_stf_lib.trex_client import CTRexClient
from trex.astf.api import *
from trex_stl_lib.api import *

from influxdb import InfluxDBClient


(opts, args) = get_args()


def cases(cases):
    """Декоратор для запуска тесткейса с несколькими параметрами"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    logging.info(f"[{func.__name__}]")
                    func(*new_args)
                except AssertionError:
                    raise AssertionError(f"{new_args}")

        return wrapper

    return decorator


class ServerManager:
    def __init__(self):
        self.master_clients = []

    @cases(TREX_INSTANCES)
    def set_master_client(self, trex_info):
        # logging.info(trex_info)
        client = CTRexClient(
            trex_info["trex_ip"],
            master_daemon_port=trex_info["master_daemon"],
            trex_daemon_port=trex_info["daemon_ports"],
            trex_zmq_port=trex_info["trex_sync_port"],
        )
        self.master_clients.append(client)


class TestManager:
    CLIENTS = []
    MODE = "stl"

    def __init__(self):
        self.ports = [0, 1]
        self.psize = UDP_PAYLOAD_SIZE
        self.speed = 0
        self.client_class = None
        self.test_stats = {}

    @classmethod
    @cases(TREX_INSTANCES)
    def set_base_client(cls, trex_info):
        client_class = STLClient if cls.MODE == "stl" else ASTFClient
        client = client_class(
            server=trex_info["trex_ip"],
            sync_port=trex_info["trex_sync_port"],
            async_port=trex_info["trex_async_port"],
        )
        cls.CLIENTS.append(client)

    @cases(CLIENTS)
    def connect(self, trex_client):
        trex_client.connect()
        # logging.info(f'{trex_client.server} connect ok')

    @cases(CLIENTS)
    def disconnect(self, trex_client):
        trex_client.disconnect()
        # logging.info(f'{trex_client.server} disconnect ok')

    @cases(CLIENTS)
    def probe_trex(self, trex_client):
        probe = trex_client.probe_server()
        logging.info(f"{probe}")

    @cases(CLIENTS)
    def acquire_ports(self, trex_client):
        trex_client.reset(ports=self.ports)

    @cases(CLIENTS)
    def setup_ports(self, trex_client):
        trex_client.set_port_attr(self.ports, promiscuous=True)

    @cases(CLIENTS)
    def stl_load_traffic_profile(self, trex_client):
        for port in self.ports:
            path = PROFILE
            profile = STLProfile.load_py(path, port_id=port)
            profile.p_size = self.psize
            profile.direction = port
            s = profile.get_streams()
            trex_client.add_streams(s, ports=port)

    @cases(CLIENTS)
    def stl_start_traffic(self, trex_client):
        trex_client.start(ports=self.ports, mult=f"{MIN_SPEED}{SPEED_UNITS}")
        self.speed = MIN_SPEED
        self.test_stats[f"{trex_client.ctx.server}:{trex_client.ctx.sync_port}"] = []

    @cases(CLIENTS)
    def stl_update_traffic(self, trex_client):
        self.speed += STEP
        trex_client.update(ports=self.ports, mult=f"{self.speed}{SPEED_UNITS}")

    @cases(CLIENTS)
    def stl_stop_traffic(self, trex_client):
        trex_client.stop(ports=self.ports)

    @cases(CLIENTS)
    def stl_get_statistic(self, trex_client):
        stats = trex_client.get_stats()
        temp = {
            "measurement": "generator_stats",
            "time": datetime.datetime.utcnow(),
            "tags": {
                "server": f"{trex_client.ctx.server}:{trex_client.ctx.sync_port}",
            },
            "fields": {
                "tx_mbps": stats["total"].get("tx_bps_L1") / 1000000,
                "rx_mbps": stats["total"].get("rx_bps_L1") / 1000000,
                "pps": stats["global"].get("tx_pps"),
                "cpu": stats["global"].get("cpu_util_raw"),
            },
        }

        self.test_stats[f"{trex_client.ctx.server}:{trex_client.ctx.sync_port}"].append(
            temp
        )


def test_stl_breaking_point(tst_mng, db_mng):
    tst_mng.acquire_ports()
    tst_mng.setup_ports()
    tst_mng.stl_load_traffic_profile()
    tst_mng.stl_start_traffic()
    while tst_mng.speed < MAX_SPEED:
        time.sleep(DURATION)
        tst_mng.stl_get_statistic()
        for generator in TREX_INSTANCES:
            json_payload = []
            data = tst_mng.test_stats[
                f'{generator["trex_ip"]}:{generator["trex_sync_port"]}'
            ][-1]
            logging.info(f"{data}")
            json_payload.append(data)
            db_mng.write_points(json_payload, database="mydb")
        tst_mng.stl_update_traffic()
    tst_mng.stl_stop_traffic()
    # test
    # result = db_mng.query('select * from total_megabits;', database='mydb')
    # print(result)


def main(trex_mode):
    # influx
    db_mng = InfluxDBClient("localhost", 8086, "admin", "admin")
    db_mng.create_database("mydb")

    # run trex
    trex_mng = ServerManager()
    # trex_mng.check_connection_to_trex() # use other built in funcs
    trex_mng.set_master_client()

    # функционал для запуска,перезапуска трекс, можно использовать, когда надо поменять режим или поднять сервак
    for count, client in enumerate(trex_mng.master_clients):
        logging.info(f'check Trex from {TREX_INSTANCES[count]["cfg"]}')
        assert client.check_server_connectivity() is True
        assert client.check_master_connectivity() is True
        assert client.is_trex_daemon_running() is True
        if client.get_running_status()["state"].value == 1:
            client.restart_trex_daemon()
            # client.kill_all_trexes() # kill all trex processes not only belongint to this daemon
            if trex_mode == "stl":
                client.start_stateless(cfg=TREX_INSTANCES[count]["cfg"], iom=1)
            else:
                client.start_astf(cfg=TREX_INSTANCES[count]["cfg"], iom=1)

    # run test
    TestManager.MODE = trex_mode
    tst_mng = TestManager()
    tst_mng.set_base_client()
    # for client in TestManager.CLIENTS:
    #     client.connect()
    #     print('connected')
    #     client.disconnect()
    tst_mng.probe_trex()
    tst_mng.connect()
    # test
    test_stl_breaking_point(tst_mng, db_mng)
    tst_mng.disconnect()


if __name__ == "__main__":
    # op = OptionParser()
    # op.add_option("-l", "--logfile", action="store", default=None)
    # op.add_option("-m", "--mode", action="store", default='stl')
    # (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.logfile, level=logging.INFO)
    main(opts.mode)
