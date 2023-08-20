# how to
1. configure a stand from a scheme below
![SCHEME!](https://github.com/ckamone/otus_pro_coursework/blob/master/doc/images/scheme.png)

2. Download and install trex to yours generator server\
`wget --no-cache --no-check-certificate https://trex-tgn.cisco.com/trex/release/v3.03`
`tar -xzvf latest`
you can find instructions in trex installation [manual](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_download_and_installation)

2. create cfg

3. run inbuilt trex daemon
```
# server 1
python3 master_daemon.py -p 8091 --trex-daemon-port 8090 start;
python3 ./trex_daemon_server -p 8090 start 
# server 2
python3 master_daemon.py -p 8093 --trex-daemon-port 8092 start;
python3 ./trex_daemon_server -p 8092 start 
...
```

4. create python environment\
`python3 -m venv venv`\
`source venv/bin/activate`

5. install requirements\
`pip install requirements.txt`

6. install docker and run influxdb via docker compose
docker compose up -d

7. get trex APIs
export PYTHONPATH=/home/user/coursework/v3.03/automation/trex_control_plane/interactive/;
export PYTHONPATH=${PYTHONPATH}:/home/user/coursework/v3.03/automation/trex_control_plane/stf

8. run test
python3 main.py


