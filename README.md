# Pymavrest

## Installation
```bash
cd $HOME
git clone https://github.com/mustafa-gokce/pymavrest.git
cd pymavrest/
/usr/bin/python3 -m pip install -r requirements.txt
```

## Usage

### Run

```bash
/usr/bin/python3 pymavrest.py
 ```

### Endpoints

#### Get all messages

```bash
curl http://127.0.0.1:2609/get/message/all
```

Sample data can be found in the [sample.json](sample/get_message_all.json) file.

```bash
curl https://raw.githubusercontent.com/mustafa-gokce/pymavrest/main/sample.json
```

#### Get a specific message by name

```bash
curl http://127.0.0.1:2609/get/message/GLOBAL_POSITION_INT
```

```json
{"alt":584070,"hdg":35196,"lat":-353632620,"lon":1491652373,"relative_alt":-17,"statistics":{"average_frequency":3.992716958686398,"counter":938,"duration":234.92774712200026,"first":1658392158.7851973,"first_monotonic":6634.220171939,"instant_frequency":3.978920063475837,"last":1658392393.7129443,"last_monotonic":6869.147919061,"latency":0.25132447600026353},"time_boot_ms":2327066,"vx":1,"vy":-1,"vz":0}
```

#### Get a specific message by message id

```bash
curl http://127.0.0.1:2609/get/message/33
```

#### Get a specific message field by message name

```bash
curl http://127.0.0.1:2609/get/message/GLOBAL_POSITION_INT/relative_alt
```

```json
{"relative_alt":-17}
```

#### Get a specific message field by message id

```bash
curl http://127.0.0.1:2609/get/message/33/alt
```

```json
{"alt":584070}
```

#### Get all parameters

```bash
curl http://127.0.0.1:2609/get/parameter/all
```

#### Get a specific parameter by name

```bash
curl http://127.0.0.1:2609/get/parameter/STAT_RUNTIME
```

```json
{"STAT_RUNTIME":{"statistics":{"average_frequency":0.04563327537308594,"counter":3,"duration":43.82766706199618,"first":1659120473.6298168,"first_monotonic":41638.127151403,"instant_frequency":0.03223455110705248,"last":1659120517.4574845,"last_monotonic":41681.954818465,"latency":31.022612868997385},"value":8897.0}}
```

#### Get all plan

```bash
curl http://127.0.0.1:2609/get/plan/all
```

#### Get a specific mission plan item by id

```bash
curl http://127.0.0.1:2609/get/plan/1
```

```json
{"autocontinue":1,"command":22,"current":0,"frame":3,"mission_type":0,"param1":0.0,"param2":0.0,"param3":0.0,"param4":0.0,"seq":1,"statistics":{"average_frequency":0,"counter":1,"duration":0,"first":1659097224.3198915,"first_monotonic":20229.831076511,"instant_frequency":0,"last":1659097224.3198915,"last_monotonic":20229.831076511,"latency":0},"target_component":0,"target_system":255,"x":0,"y":0,"z":50.0}
```

#### Get all fence

```bash
curl http://127.0.0.1:2609/get/fence/all
```

#### Get a specific fence item by id

```bash
curl http://127.0.0.1:2609/get/fence/1
```

```json
{"count":6,"idx":1,"lat":-35.35980224609375,"lng":149.16319274902344,"statistics":{"average_frequency":0,"counter":1,"duration":0,"first":1660055296.6694324,"first_monotonic":28660.054151877,"instant_frequency":0,"last":1660055296.6694324,"last_monotonic":28660.054151877,"latency":0},"target_component":0,"target_system":255}
```

#### Get all rally

```bash
curl http://127.0.0.1:2609/get/rally/all
```

#### Get a specific rally item by id

```bash
curl http://127.0.0.1:2609/get/rally/0
```

```json
{"alt":100,"break_alt":40,"count":2,"flags":0,"idx":0,"land_dir":0,"lat":-353608816,"lng":1491632271,"statistics":{"average_frequency":0,"counter":1,"duration":0,"first":1660120011.4000502,"first_monotonic":6584.331569675,"instant_frequency":0,"last":1660120011.4000502,"last_monotonic":6584.331569675,"latency":0},"target_component":0,"target_system":255}
```

#### Post `COMMAND_INT` command message to vehicle

To move to a position in `GUIDED` mode using `COMMAND_INT` command message:

```bash
curl -i -X POST -H "Content-Type: application/json" -d '{"target_system": 0, "target_component":0, "frame":6, "command":192, "current":0, "autocontinue":0,"param1":1, "param2":0, "param3":0, "param4":0, "x":-353613322, "y":1491611469, "z":10}' http://127.0.0.1:2609/post/command_int
```

```json
{"command":"COMMAND_INT","connected":true,"sent":true,"valid":true}
```

#### Post `COMMAND_LONG` command message to vehicle

To arm the vehicle using `COMMAND_LONG` command message:

```bash
curl -i -X POST -H "Content-Type: application/json" -d '{"target_system": 0, "target_component":0, "command":400, "confirmation":0, "param1":1, "param2":0, "param3":0, "param4":0, "param5":0, "param6":0, "param7":0}' http://127.0.0.1:2609/post/command_long
```

```json
{"command":"COMMAND_LONG","connected":true,"sent":true,"valid":true}
```

### Advanced run and query

```bash
/usr/bin/python3 pymavrest.py --host="127.0.0.1" --port=2609 --master="udpin:127.0.0.1:14550" --timeout=5.0 --drop=5.0 --white="GLOBAL_POSITION_INT,ATTITUDE,VFR_HUD" --black="VFR_HUD" --param=True --plan=True --fence=True --rally=True
```

```bash
curl http://127.0.0.1:2609/get/message/all
```

```json
{"ATTITUDE":{"pitch":-0.0009615588351152837,"pitchspeed":-0.00013825629139319062,"roll":-0.0007417603628709912,"rollspeed":-0.0001102022361010313,"statistics":{"average_frequency":3.992590263518338,"counter":6,"duration":1.2523198400012916,"first":1660055296.9819467,"first_monotonic":28660.366665863,"instant_frequency":4.073447899117448,"last":1660055298.2342658,"last_monotonic":28661.618985703,"latency":0.24549227700117626},"time_boot_ms":14405031,"yaw":-0.13958577811717987,"yawspeed":-0.0006176364840939641},"GLOBAL_POSITION_INT":{"alt":584070,"hdg":35201,"lat":-353632620,"lon":1491652373,"relative_alt":-17,"statistics":{"average_frequency":3.9926913529235,"counter":6,"duration":1.2522881330005475,"first":1660055296.98224,"first_monotonic":28660.366959684,"instant_frequency":4.075237972571812,"last":1660055298.2345283,"last_monotonic":28661.619247817,"latency":0.24538444300196716},"time_boot_ms":14405031,"vx":1,"vy":-1,"vz":0}}
```

## Arguments

| Argument | Type  | Default                 | Help                                                                                         |
|----------|-------|-------------------------|----------------------------------------------------------------------------------------------|
| host     | str   | "127.0.0.1"             | Pymavrest server IP address                                                                  |
| port     | int   | 2609                    | Pymavrest server port number                                                                 |
| master   | str   | "udpin:127.0.0.1:14550" | Standard MAVLink connection string                                                           |
| timeout  | float | 5.0                     | Try to reconnect after this seconds when no message is received, zero means do not reconnect |
| drop     | float | 5.0                     | Drop non-periodic messages after this seconds, zero means do not drop                        |
| white    | str   | ""                      | Comma separated white list to filter messages, empty means all messages are in white list    |
| black    | str   | ""                      | Comma separated black list to filter messages                                                |
| param    | bool  | True                    | Fetch parameters                                                                             |
| plan     | bool  | True                    | Fetch plan                                                                                   |
| fence    | bool  | True                    | Fetch fence                                                                                  |
| rally    | bool  | True                    | Fetch rally                                                                                  |