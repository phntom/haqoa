import logging
import os
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory

import pushy
import requests

from haqoa.consts import appId, androidId
from haqoa.logs import logging_setup

log = logging.getLogger(__name__)
logging_setup(log)


def config_pushy(token, auth, areas):
    pushy.setEnterpriseConfig("https://pushy.ioref.app", os.getenv('OREF_MQTT', "mqtt-{timestamp}.ioref.io"))
    pushy.config.set('mqtt', 'enterprisePortNumber', '443')
    pushy.config.set('storageKeys', 'token', token)
    pushy.config.set('storageKeys', 'tokenAuth', auth)
    pushy.config.set('storageKeys', 'tokenAppId', appId)
    pushy.config.set('sdk', 'version', '10117')
    pushy.config.set('sdk', 'platform', 'android')
    pushy.setHeartbeatInterval(300)
    device_token = pushy.register({'appId': appId, 'app': 'com.ioref.meserhadash', 'androidId': androidId})
    log.info("Device token: %s", device_token)
    pushy.setNotificationListener(background_notification_listener)
    test_areas = os.getenv('TEST_AREAS', '').strip().split(',')
    if test_areas and test_areas != ['']:
        areas.extend(test_areas)

    log.info("Subscribing to areas: %s", ','.join(areas))
    pushy.subscribe(areas)


def register():
    log.warning("Registering device...")
    response = requests.post("https://pushy.ioref.app/register",
                             headers={"Content-Type": "application/json"},
                             json={
                                 "appId": appId,
                                 "app": "com.alert.meserhadash",
                                 "androidId": androidId,
                                 "sdk": 10117,
                                 "platform": "android"
                             })
    response.raise_for_status()
    j = response.json()
    log.info("Registered device: token: %s | auth %s", j['token'], j['auth'])
    return j['token'], j['auth']


def background_notification_listener(data):
    logging.warning('Received notification: %s', data)
    target_areas = set(os.getenv('ALERT_AREAS', '').strip().split(','))
    alert_areas = set(data.get('citiesIds', '').split(','))
    delay = None
    data['mqtt'] = os.getenv('OREF_MQTT', "mqtt-{timestamp}.ioref.io")

    if 'time' in data:
        data_time = data['time']
        data_time_tz = data_time[-5:]
        now_timestamp = datetime.strptime(datetime.now().replace(microsecond=0).isoformat() + data_time_tz,
                                          "%Y-%m-%dT%H:%M:%S%z")
        timestamp = datetime.strptime(data_time, "%Y-%m-%dT%H:%M:%S%z")
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

    if not alert_areas.intersection(target_areas):
        log.warning("Skipping alert, not in target areas.")
    else:
        send_webhook(data)

    if delay.total_seconds() > 2:
        log.warning("Alert delivery time %d seconds. Resetting subscription", delay.total_seconds())
        test_areas = os.getenv('TEST_AREAS', '').strip().split(',')
        if test_areas and test_areas != ['']:
            test_areas.extend(target_areas)
        else:
            test_areas = target_areas
        log.info("Resubscribing to areas: %s", ','.join(test_areas))
        pushy.unsubscribe(test_areas)
        pushy.subscribe(test_areas)


def send_webhook(data):
    webhook_url = os.getenv('WEBHOOK_URL', '').strip()
    if webhook_url:
        requests.post(webhook_url, json=data)


def run():
    areas = os.getenv('ALERT_AREAS', '').strip().split(',')
    if not areas:
        log.critical("No areas to subscribe to, aborting")
        exit(9)

    with TemporaryDirectory() as tmpdir:
        log.info("Changing directory to %s", tmpdir)
        os.chdir(tmpdir)

        token, auth = os.getenv('OREF_TOKEN', ''), os.getenv('OREF_AUTH', '')
        if not token:
            token, auth = register()
        config_pushy(token, auth, areas)
        pushy.listen()
        pushy.loop_forever()
