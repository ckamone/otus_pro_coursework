# how to
1. configure a stand from a scheme below
![SCHEME!](https://github.com/ckamone/otus_pro_coursework/blob/master/doc/images/scheme.png)

2. set up dut via ansible\
`ansible-playbook -vvvv -i inventory/hosts playbook/tst.yml --ask-pass`

3. Download and install trex to yours generator server\
`mkdir /opt/trex`\
`cd /opt/trex`\
`wget --no-cache --no-check-certificate https://trex-tgn.cisco.com/trex/release/v3.03`\
`tar -xzvf v3.03`\
you can find instructions in trex installation [manual](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_download_and_installation)

4. create trex server cfg\
`./dpdk_setup_ports.py -i`\
__/etc/trex_cfg.yaml__ will be created.\
Example:
```
### Config file generated by dpdk_setup_ports.py ###

- version: 2
  interfaces: ['17:00.0', '17:00.1']
  port_info:
      - dest_mac: b4:96:91:f6:51:95 # MAC OF LOOPBACK TO IT'S DUAL INTERFACE
        src_mac:  b4:96:91:f6:51:94
      - dest_mac: b4:96:91:f6:51:94 # MAC OF LOOPBACK TO IT'S DUAL INTERFACE
        src_mac:  b4:96:91:f6:51:95

  platform:
      master_thread_id: 0
      latency_thread_id: 1
      dual_if:
        - socket: 0
          threads: [2,3,4,5,6,7,8,9]
```
you will need to add __zmq_rpc_port__, __zmq_pub_port__ and unique __prefix__ (server setup name) to cfg file
5. run inbuilt trex daemon
```
# server 1
python3 master_daemon.py -p 8091 --trex-daemon-port 8090 start;
python3 ./trex_daemon_server -p 8090 start 
# server 2
python3 master_daemon.py -p 8093 --trex-daemon-port 8092 start;
python3 ./trex_daemon_server -p 8092 start 
...
```

6. download this repo and create python environment\
`python3 -m venv venv`\
`source venv/bin/activate`

7. install requirements\
`pip install requirements.txt`

8. install docker and run docker compose\
`docker compose up -d`

9. configure grafana DB source and dashboard

10. configure test params in __./test_config/config.py__

11. get trex APIs
```
export PYTHONPATH=/home/user/coursework/v3.03/automation/trex_control_plane/interactive/;
export PYTHONPATH=${PYTHONPATH}:/home/user/coursework/v3.03/automation/trex_control_plane/stf
```

12. run test\
`python3 main.py -l ./log/test1.txt -m stl`

13. watch live stats in grafana
![SCHEME!](https://github.com/ckamone/otus_pro_coursework/blob/master/doc/images/grafana_example.png)