from trex_stl_lib.api import *
import argparse


class STLS1(object):
    def __init__(self) -> None:
        self.p_size = 10
        self.direction = 0

    def create_stream(self):
        if self.direction == 0:
            mac_src = "01:80:c2:00:00:10"
            mac_dst = "01:80:c2:00:00:11"
            ip_src = "16.0.0.1"
            ip_dst = "48.0.0.1"
        else:
            mac_src = "01:80:c2:00:00:11"
            mac_dst = "01:80:c2:00:00:10"
            ip_src = "48.0.0.1"
            ip_dst = "16.0.0.1"
        return STLStream(
            packet=STLPktBuilder(
                pkt=Ether(src=mac_src, dst=mac_dst)
                / IP(src=ip_src, dst=ip_dst)
                / UDP(dport=12, sport=1025)
                / (self.p_size * "x")
            ),
            mode=STLTXCont(),
        )

    def get_streams(self, tunables, **kwargs):
        parser = argparse.ArgumentParser(
            description="Argparser for {}".format(os.path.basename(__file__)),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        args = parser.parse_args(tunables)
        # create 1 stream
        return [self.create_stream()]


# dynamic load - used for trex console or simulator
def register():
    return STLS1()
