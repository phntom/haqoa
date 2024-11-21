import json
import logging
import os
from datetime import datetime, timedelta

import pushy
import requests

from haqoa import metrics
from haqoa.consts import (app_id, android_id, pushy_endpoint, oref_mqtt_hostname, oref_app, oref_register_url,
                          oref_platform, pushy_sdk_version, time_format)
from haqoa.logs import logging_setup

log = logging.getLogger(__name__)
logging_setup(log)


def config_pushy(token, auth, areas):
    mqtt_host = os.getenv('OREF_MQTT', oref_mqtt_hostname)

    metrics.client_info.labels(token=token, auth=auth, mqtt_host=mqtt_host).set(1)

    pushy.setEnterpriseConfig(pushy_endpoint, mqtt_host)
    pushy.config.set('mqtt', 'enterprisePortNumber', '443')
    pushy.config.set('storageKeys', 'token', token)
    pushy.config.set('storageKeys', 'tokenAuth', auth)
    pushy.config.set('storageKeys', 'tokenAppId', app_id)
    pushy.config.set('sdk', 'version', pushy_sdk_version)
    pushy.config.set('sdk', 'platform', oref_platform)
    pushy.setHeartbeatInterval(300)
    device_token = pushy.register({'appId': app_id, 'app': oref_app, 'androidId': android_id})
    log.info("Device token: %s", device_token)
    pushy.setNotificationListener(background_notification_listener)
    test_areas = os.getenv('TEST_AREAS', '').strip().split(',')
    if test_areas and test_areas != ['']:
        areas.extend(test_areas)
    log.info("Subscribing to areas: %s", ','.join(areas))
    pushy.subscribe(areas)
    for area in areas:
        metrics.target_area.labels(area_id=area).set(1)


def register():
    log.warning("Registering device...")
    response = requests.post(oref_register_url,
                             headers={"Content-Type": "application/json"},
                             json={
                                 "appId": app_id,
                                 "app": oref_app,
                                 "androidId": android_id,
                                 "sdk": 10117,
                                 "platform": oref_platform,
                             })
    response.raise_for_status()
    j = response.json()
    log.info("Registered device: token: %s | auth %s", j['token'], j['auth'])
    return j['token'], j['auth']


def background_notification_listener(data):
    mqtt_host = data['_mqtt'] = os.getenv('OREF_MQTT', oref_mqtt_hostname)
    logging.warning('Received notification: %s', json.dumps(data, indent=2, sort_keys=True))
    metrics.received.labels(mqtt_host=mqtt_host).inc()

    target_areas = set(os.getenv('ALERT_AREAS', '').strip().split(','))
    alert_areas = set(data.get('citiesIds', '').split(','))
    delay = None

    if 'time' in data:
        data_time = data['time']
        data_time_tz = data_time[-5:]
        now_timestamp = datetime.strptime(datetime.now().replace(microsecond=0).isoformat() + data_time_tz, time_format)
        timestamp = datetime.strptime(data_time, time_format)
        time_in_10m = timestamp + timedelta(minutes=10)

        data['time_add_10m'] = time_in_10m.isoformat()
        data['time_add_10m_epoch'] = time_in_10m.timestamp()

        add_seconds = int(os.getenv('ADD_SECONDS', '0').strip())
        if add_seconds:
            time_add_seconds = timestamp + timedelta(seconds=add_seconds)
            data['time_add_seconds'] = time_add_seconds.isoformat()
            data['time_add_seconds_epoch'] = time_add_seconds.timestamp()
            seconds_remain = int((time_add_seconds - now_timestamp).total_seconds())
            data['time_seconds_remain'] = seconds_remain
            if seconds_remain < 0:
                log.warning("Skipping alert, time already passed %d seconds ago. %s", seconds_remain, data)
                return
        elif time_in_10m < now_timestamp:
            log.warning("Skipping alert, time already passed 10 minutes ago. %s", data)
            return

        delay = now_timestamp - timestamp
        metrics.delay.labels(mqtt_host=mqtt_host).set(delay.total_seconds())

    if not alert_areas.intersection(target_areas):
        log.warning("Skipping alert, not in target areas.")
        metrics.skipped.labels(mqtt_host=mqtt_host).inc()
    else:
        send_webhook(data)
        metrics.processed.labels(mqtt_host=mqtt_host).inc()

    if delay.total_seconds() > 1:
        log.info("Alert delivery time %d seconds.", delay.total_seconds())
        # test_areas = os.getenv('TEST_AREAS', '').strip().split(',')
        # if test_areas and test_areas != ['']:
        #     test_areas.extend(target_areas)
        # else:
        #     test_areas = target_areas
        # log.info("Resubscribing to areas: %s", ','.join(test_areas))
        # pushy.unsubscribe(test_areas)
        # pushy.subscribe(test_areas)


def send_webhook(data):
    webhook_url = os.getenv('WEBHOOK_URL', '').strip()
    if webhook_url:
        requests.post(webhook_url, json=data)


def run():
    areas = os.getenv('ALERT_AREAS', '').strip().split(',')
    if not areas:
        log.critical("No areas to subscribe to, aborting")
        exit(9)

    token, auth = os.getenv('OREF_TOKEN', ''), os.getenv('OREF_AUTH', '')
    if not token:
        token, auth = register()
    config_pushy(token, auth, areas)
    pushy.listen()
    metrics.expose()
    pushy.loop_forever()
