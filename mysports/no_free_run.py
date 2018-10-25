import json
import random
import time
from datetime import datetime, timedelta

from mysports.original_json import no_free_data, host
from mysports.sports import *
from path_plan.plan import path_plan


def no_free_run(userid: str, ses, extra_pn=1):
    data = json.dumps({"initLocation": "121.85284044053819,30.911461588541666", "type": "1", "userid": userid})

    res = ses.get(host + '/api/run/runPage', params={'sign': get_md5_code(data), 'data': data.encode('ascii')})

    resj = res.json()['data']

    #red, green
    red, green = 2, 2
    no_free_data['bNode'] = resj['ibeacon'][:red]
    no_free_data['tNode'] = resj['gpsinfo'][:green]
    position_info = no_free_data['bNode'][0]['position']
    start_point = gps_point(float(position_info['latitude']), float(position_info['longitude']))

    # pass_by_ps : List[gps_point]
    pass_by_ps = gps_point_list([start_point.zouzou(strip=0.003) for x in range(extra_pn)])

    # reformat bnode, tnode ;  collect passby points
    for node in no_free_data['bNode']:
        pos = node['position']
        pos['latitude'] = float(pos['latitude'])
        pos['longitude'] = float(pos['longitude'])
        pos['speed'] = 0.0
        node['position'] = pos

        pass_by_ps.append(gps_point(pos['latitude'], pos['longitude']))

    for pos in no_free_data['tNode']:
        pos['latitude'] = float(pos['latitude'])
        pos['longitude'] = float(pos['longitude'])
        pos['speed'] = 0.0

        pass_by_ps.append(gps_point(pos['latitude'], pos['longitude']))

    #path plan
    plan = path_plan(pass_by_ps)
    dis = plan['distance']
    path = plan['path']

    #reformat path
    tmp = []
    for p in path:
        tmp.append({'latitude':p['lat'], 'longitude':p['lng']})
    path = tmp

    # insert path, dis, duration, speed into x
    speed = random.randint(300, 500) # seconds per km
    duration = dis * speed  #seconds
    # to 'minutes'seconds'microseconds'
    speed = "%s'%s''"%(speed//60,speed - speed//60 * 60)
    startTime = (datetime.now() - timedelta(seconds=duration)).strftime("%Y-%m-%d %H:%M:%S")

    # peisu = 1000 / (bupin * bufu)
    bupin = random.uniform(120, 140)

    no_free_data['endTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    no_free_data['userid'] = userid
    no_free_data['runPageId'] = resj['runPageId']

    no_free_data['real'] = str(dis * 1000)
    no_free_data['duration'] = str(duration)
    no_free_data['speed'] = speed
    no_free_data['track'] = path
    no_free_data['startTime'] = startTime
    no_free_data['buPin'] = '%.1f' % bupin

    xs = json.dumps(no_free_data)
    # time.sleep(duration)
    r = ses.post(host + '/api/run/saveRunV2', data={'sign': get_md5_code(xs), 'data': xs.encode('ascii')})
    print(r.content.decode('utf-8'))
    return dis