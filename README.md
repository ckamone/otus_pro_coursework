1. get trex
wget --no-cache --no-check-certificate https://trex-tgn.cisco.com/trex/release/latest
tar -xzvf latest

2. create cfg

3. run trex daemon
python3 master_daemon.py -p 8091 --trex-daemon-port 8090 start
python3 ./trex_daemon_server -p 8090 start 
...

4. make env
python3 -m venv venv
source venv/bin/activate

5. install requirements
pip install requirements.txt

6. get trex APIs
export PYTHONPATH=/home/user/coursework/v3.03/automation/trex_control_plane/interactive/
export PYTHONPATH=${PYTHONPATH}:/home/user/coursework/v3.03/automation/trex_control_plane/stf

7. run test
python3 main.py