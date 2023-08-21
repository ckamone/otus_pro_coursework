# Otus coursework

## description
Cisco TREX — высокопроизводительный генератор трафика. Для своей работы использует dpdk. Аппаратные требования — 64-bit архитектура, совместимая сетевая карта, поддерживаемые ос * Fedora 18-20, 64-bit kernel (not 32-bit) * Ubuntu 14.04.1 LTS, 64-bit kernel (not 32-bit). Вы можете запустить на другом линуксе, запилив себе необходимые драйвера и собрав свою версию из файлов, которые лежат в репозитории на гитхабе, здесь все стандартно.

## DPDK
Data Plane Development Kit (DPDK), изначально разработанный Intel и переданный в открытое сообщество.
DPDK это фреймворк который предоставляет набор библиотек и драйверов для ускорения обработки пакетов в приложениях, работающих на архитектуре Intel. DPDK поддерживается на любых процессорах Intel от Atom до Xeon, любой разрядности и без ограничения по количеству ядер и процессоров. В настоящее время DPDK портируется и на другие архитектуры, отличные от x86 — IBM Power 8, ARM и др.
Если не углубляться в технические подробности, DPDK позволяет полностью исключить сетевой стек Linux из обработки пакетов. Приложение, работающее в User Space, напрямую общается с аппаратным обеспечением.
Помимо поддержки физических карточек имеется возможность работать с paravirtualized картами VMware (VMXNET /
VMXNET3, Connect using VMware vSwitch) и E1000 (VMware/KVM/VirtualBox).

## deploy
1. В данном проекте я хотел реализовать легко маштабируемую схему, в которой трафик с помощью python-менеджера запускается с нескольких генератов. Генераторы могут быть развернуты на отдельных ВМ/серверах.
![SCHEME!](https://github.com/ckamone/otus_pro_coursework/blob/master/doc/images/scheme.png)

2. Скачаем, распакуем, соберем trex.\
`mkdir /opt/trex`\
`cd /opt/trex`\
`wget --no-cache --no-check-certificate https://trex-tgn.cisco.com/trex/release/v3.03`\
`tar -xzvf v3.03`\
Более подробная инструкуция в офичиальном [мануале](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_download_and_installation)

3. Интерфейсы, с которых будет производиться тестирование, необходимо вытащить из линукса и передать под управление dpdk, для этого необходимо выполнить команду, которая сгенерирует конфигурационный файл сервера TREX.\
`./dpdk_setup_ports.py -i`\
__/etc/trex_cfg.yaml__ will be created.\
Пример:
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
Далее нужно будет дополнить конфиг значениями __zmq_rpc_port__, __zmq_pub_port__ (можно взять за основу пример из repo)

4. Процедура запуска демон процессов. Демон процессы запускаются уже встроенными в TREX скриптами
```
# server 1
python3 master_daemon.py -p 8091 --trex-daemon-port 8090 start;
python3 ./trex_daemon_server -p 8090 start 
# server 2
python3 master_daemon.py -p 8093 --trex-daemon-port 8092 start;
python3 ./trex_daemon_server -p 8092 start 
...
```

5. Скачайте репозиторий и настройте окружение для python\
`python3 -m venv venv`\
`source venv/bin/activate`

6. Установка зависимостей\
`pip install requirements.txt`

7. Установить настройки на DUT (Device Under Test) с помощью ansible\
`ansible-playbook -vvvv -i inventory/hosts playbook/tst.yml --ask-pass`

8. С помощью docker compose поднять influxdb и grafana\
`docker compose up -d`

9. Grafana запускается на 3000 порту. необходимо перейти и настроить в ней источних данных и дэшборд. (__admin/admin__)

10. Параметры теста задаются здесь __./test_config/config.py__\
TREX_INSTANCES - список инстансов TREX. Список состоит из словаря с параметрами инстанса TREX.\
PROFILE - путь к профайлу трафика\
SPEED_UNITS - единица измерения скорости\
MIN_SPEED - стартовая скорость\
MAX_SPEED - пороговая скорость\
STEP - шаг прибавления скорости\
DURATION - длительность шага\
UDP_PAYLOAD_SIZE -размер payload UDP пакета

11. перед запуском настроить переменные окружения для API TREX'а
```
export PYTHONPATH=/home/user/coursework/v3.03/automation/trex_control_plane/interactive/;
export PYTHONPATH=${PYTHONPATH}:/home/user/coursework/v3.03/automation/trex_control_plane/stf
```

12. запуск теста\
`python3 main.py -l ./log/test1.txt -m stl`
-l - путь к лог файлу (опционально)\
-m - режим работы (stl - stateless, astf - advanced statefull)

13. Проверка работы live-статистики в grafana
![SCHEME!](https://github.com/ckamone/otus_pro_coursework/blob/master/doc/images/grafana_example2.png)
Пока реализовано 3 графика. Это график скорости TX, RX; график загрузки CPU сервера TREX; график количества PPS (пакетов в секунду).