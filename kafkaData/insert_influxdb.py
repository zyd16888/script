# influxdb 插入数据

from influxdb import InfluxDBClient
import time
import random


client = InfluxDBClient(host="127.0.0.1", port=8086, database="mddp_data")

# 表名
measurement = "sgyy_data"

pcode = [
    "s60device1test01",
    "s60device2test01",
    "s60device2test02",
    "s60device3test01",
    "s60device4test01",
    "s60device4test02",
    "S61device1test01",
    "S61device2test01",
    "S61device2test02",
    "S61device3test01",
    "S61device4test01",
    "S61device4test02",
    "S62device1test01",
    "S62device2test01",
    "S62device2test02",
    "S62device3test01",
    "S62device4test01",
    "S62device4test02",
]

name_list = [
    "能耗1560_01_01",
    "能耗1560_02_01",
    "能耗1560_02_02",
    "能耗1560_03_01",
    "能耗1560_04_01",
    "能耗1560_04_02",
    "能耗1561_01_01",
    "能耗1561_02_01",
    "能耗1561_02_02",
    "能耗1561_03_01",
    "能耗1561_04_01",
    "能耗1561_04_02",
    "能耗1562_01_01",
    "能耗1562_02_01",
    "能耗1562_02_02",
    "能耗1562_03_01",
    "能耗1562_04_01",
    "能耗1562_04_02",
]


start_time = "2018-10-01 00:00:00"
end_time = "2022-05-01 00:00:00"

# 毫秒级时间戳
time_stamp = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")) * 1000)

end_time_stamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")) * 1000)

# 生成值
data_value = []
for i in range(0, len(pcode)):
    data_value.append(random.uniform(50, 100))

while True:
    # 构造数据
    data = []
    # 时间戳转换为时间(获取日期)
    day_time = time.strftime("%Y%m%d", time.localtime(time_stamp / 1000))
    year_time = time.strftime("%Y", time.localtime(time_stamp / 1000))
    for i in range(0, len(pcode)):
        # data_value = random.uniform(10, 100)
        data.append(
            {
                "measurement": measurement,
                "tags": {
                    "ppcode": "ppcode",
                    "fire_alarm": None,
                    "smoke_alarm": None,
                    "temp_alarm": None,
                    "is_gas_spray": None,
                    "is_gas_out_poweroff": None,
                    "is_gas_out_error": None,
                    "is_gas_out_offline": None,
                    "fan_state": None,
                    "is_fan_poweroff": None,
                    "low_waterlevel_alarm": None,
                    "high_waterlevel_alarm": None,
                }, 
                "time": time_stamp,
            }
        )
    # 插入数据
    client.write_points(data, time_precision="ms")
    # 更新数据
    for i in range(0, len(pcode)):
        data_value[i] += 0.01
    # 时间加五分钟
    time_stamp += 300 * 1000
    # time.sleep(1)
    # 跳出循环
    print(time.strftime("%Y%m%d", time.localtime(time_stamp / 1000)))
    if time_stamp == end_time_stamp:
        break

