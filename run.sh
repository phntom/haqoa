#!/usr/bin/env bash

# register.sh
export OREF_TOKEN=xxx
export OREF_AUTH=xxx

# https://dist.meser-hadash.org.il/smart-dist/services/anonymous/segments/android?instance=1544803905&locale=iw_IL
export ADD_SECONDS=90
export ALERT_AREAS=5000023

# https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger
export WEBHOOK_URL=http://127.0.0.1:8123/api/webhook/xxx

while true; do
  .venv/bin/python main.py
done
