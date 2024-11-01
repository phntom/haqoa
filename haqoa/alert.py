import logging
import os
from datetime import datetime, timedelta

import pushy
import requests

from haqoa.consts import appId, androidId

log = logging.getLogger(__name__)


def config_pushy():
    pushy.setEnterpriseConfig("https://pushy.ioref.app", "mqtt-{timestamp}.ioref.io")
    pushy.config.set('mqtt', 'enterprisePortNumber', '443')
    pushy.config.set('storageKeys', 'token', os.getenv('OREF_TOKEN'))
    pushy.config.set('storageKeys', 'tokenAuth', os.getenv('OREF_AUTH'))
    pushy.config.set('storageKeys', 'tokenAppId', appId)
    pushy.config.set('sdk', 'version', '10117')
    pushy.config.set('sdk', 'platform', 'android')
    pushy.setHeartbeatInterval(300)
    device_token = pushy.register({'appId': appId, 'app': 'com.ioref.meserhadash', 'androidId': androidId})
    log.info("Device token: %s", device_token)
    pushy.setNotificationListener(background_notification_listener)
    areas = os.getenv('ALERT_AREAS', '').strip().split(',')
    if not areas:
        log.critical("No areas to subscribe to, aborting")
        exit(9)
    log.info("Subscribing to areas: %s", ','.join(areas))
    pushy.subscribe(areas)


def background_notification_listener(data):
    logging.warning('Received notification: %s', data)
    if 'time' in data:
        data_time = data['time']
        data_time_tz = data_time[-5:]
        now_timestamp = datetime.strptime(datetime.now().replace(microsecond=0).isoformat() + data_time_tz, "%Y-%m-%dT%H:%M:%S%z")
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

    send_webhook(data)


def send_webhook(data):
    webhook_url = os.getenv('WEBHOOK_URL', '').strip()
    if webhook_url:
        requests.post(webhook_url, json=data)


def run():
    config_pushy()
    pushy.listen()
    pushy.loop_forever()
