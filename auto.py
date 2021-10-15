import json
import requests
import os
import datetime as DT
from datetime import date
import time

HERE = os.path.dirname(os.path.abspath(__file__))

def load_conf(conf_file='pzones.json'):

    ret = {}

    with open(os.path.join(HERE, conf_file)) as conf:
        data = json.load(conf)
        ret = data

    return ret


def zonelist(campid, headers, cpa, today, status, week, month):

    zonelist = []

    if status == 0: #this one is meant to be POP

        url = 'https://ssp-api.propellerads.com/v5/adv/statistics?group_by[]=zone_id&date_from=' + str(month) + '&date_to=' + str(today) + '&campaign_id[]=' + str(campid)
        zonelist_r = requests.get(url, headers=headers)
        zonelist_z = json.loads(zonelist_r.content)
        zonelist_d = zonelist_z['result']

        for i in zonelist_d:

            spend = round(float(i['money']),3)
            clicks = i['clicks']
            conv = i['conversions']
            zone = i['zone_id']
            payout = round(float(i['payout']),2)

            if float(spend) > (5 * float(cpa)) and int(conv) < 1:
                zonelist.append(zone)

            if int(conv) > 0:
                if float(spend) > (5 * float(cpa)) and float(spend) / int(conv) > (1.2 * float(cpa)):
                    zonelist.append(zone)



    if status == 1: #this one is meant to be PUSH

        url = 'https://ssp-api.propellerads.com/v5/adv/statistics?group_by[]=zone_id&date_from=' + str(month) + '&date_to=' + str(today) + '&campaign_id[]=' + str(campid)
        zonelist_r = requests.get(url, headers=headers)
        zonelist_z = json.loads(zonelist_r.content)
        zonelist_d = zonelist_z['result']

        for i in zonelist_d:

            spend = round(float(i['money']), 3)
            clicks = i['clicks']
            conv = i['conversions']
            zone = i['zone_id']
            payout = round(float(i['payout']), 2)

            if float(spend) > (3 * float(cpa)) and int(conv) < 1:
                zonelist.append(zone)

            if int(conv) > 0:
                if float(spend) > (3 * float(cpa)) and float(spend) / int(conv) > (1.2 * float(cpa)):
                    zonelist.append(zone)


    return zonelist


def emptyzones(campid, headers, status, cpa):

    url = 'https://ssp-api.propellerads.com/v5/adv/campaigns/' + str(campid) + '/targeting/exclude/zone'
    d = "{\"zone\":" + str([]) + "}"
    r = requests.put(url, headers=headers, data=d)



def killzone(campid, headers, zones):

    url = 'https://ssp-api.propellerads.com/v5/adv/campaigns/' + str(campid) + '/targeting/exclude/zone'
    d = "{\"zone\":" + str(zones) + "}"
    r = requests.put(url, headers=headers, data=d)
    print(campid, d, r.status_code, r.reason)


def main():

    headers = {'accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ****APITOKEN****'}

    conf = load_conf()

    with open ("/var/www/binom/python/AutoOptimizer/log.txt", "w") as text_file:
        text_file.write('Executed at %s' % 
               (DT.datetime.now()))


    fmt = "%Y-%m-%d"
    today = date.today()
    week = today - DT.timedelta(days=14)
    month = today - DT.timedelta(days=30)
    today = today.strftime(fmt)

    for one in conf:
        campid = one['campaign']
        cpa = one['cpa']
        status = one['status']

        y = zonelist(campid, headers, cpa, today, status, week, month)

        if status == 0:

            x = emptyzones(campid, headers, status, cpa)

            zones = json.dumps(list(set(y)))
            if (len(zones) > 0):
                killzone(campid, headers, zones)

        else:

            x = emptyzones(campid, headers, status, cpa)

            zones = json.dumps(list(set(y)))
            if (len(zones) > 0):
                killzone(campid, headers, zones)





if __name__ == '__main__':
    main()
