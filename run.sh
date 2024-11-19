#!/usr/bin/env bash

# https://dist.meser-hadash.org.il/smart-dist/services/anonymous/segments/android?instance=1544803905&locale=iw_IL
export ADD_SECONDS=90
export ALERT_AREAS=5000023

# https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger
export WEBHOOK_URL=http://127.0.0.1:8123/api/webhook/xxx

while true; do
  sleep 1
  pgrep main.py --full --list-name | grep -q python && continue

  OREF_MQTT=mqtt-45.ioref.io .venv/bin/python main.py &
  sleep 100
  OREF_MQTT=mqtt-233.ioref.io .venv/bin/python main.py &
  sleep 100
  OREF_MQTT=mqtt-167.ioref.io .venv/bin/python main.py

done

# 51.17.111.45 mqtt-45.ioref.io
# 51.17.46.233 mqtt-233.ioref.io
# 51.17.209.167 mqtt-167.ioref.io
