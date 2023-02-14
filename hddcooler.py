import time
from datetime import datetime
from pyzabbix import ZabbixAPI
import json

#import logging
#logging.basicConfig(level=logging.DEBUG)
import RPi.GPIO as GPIO
servoPIN = 18
GPIO.setmode(GPIO.BCM)

zapi = ZabbixAPI("")
#zapi.login("zabbix user", "zabbix pass")
# You can also authenticate using an API token instead of user/pass with Zabbix >= 5.4
zapi.login(api_token='')
print("Connected to Zabbix API Version %s" % zapi.api_version())

grp = "Genie"
tempName = "Temperature"

group = zapi.hostgroup.get(filter={"name": grp}, output=["groupid"])

if len(group) > 0:
    groupValue = group[0]['groupid']

items = zapi.item.get(search={"name": tempName}, groupids=groupValue, output=["itemid"])
print(items)
# Remove  () key

for item_id in items:
    if item_id['itemid']=="":
        items.remove(item_id)
        print("Removed")

print(items)


time_till = int(time.mktime(datetime.now().timetuple()))
time_from = int(time_till - 3600)

maxTemp = 0

for item_id in items:
    # Query item's history (integer) data
    history = zapi.history.get(
        itemids=[item_id['itemid']],
        time_from=time_from,
        time_till=time_till,
        output="extend",
        sortfield="clock",
        sortorder="DESC",
        limit="1",
    )

    if not len(history):
        history = zapi.history.get(
            itemids=[item_id],
            time_from=time_from,
            time_till=time_till,
            output="extend",
            limit="1",
            history=0,
        )

    # Print out each datapoint
    for point in history:
        print(
            "{}: {}".format(
                datetime.fromtimestamp(int(point["clock"])).strftime("%x %X"),
                point["value"],
            )
        )
        if int(point["value"]) > maxTemp:
            maxTemp=int(point["value"])
print(maxTemp)
if maxTemp > 45:
    GPIO.setup(servoPIN, GPIO.OUT, initial=GPIO.HIGH)
    print("Fan start")
else:
    GPIO.setup(servoPIN, GPIO.OUT, initial=GPIO.LOW)
    print("Fan stop")
