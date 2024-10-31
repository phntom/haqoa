#!/usr/bin/env bash

set -ex
curl -X POST https://pushy.ioref.app/register \
     -H "Content-Type: application/json" \
     -d '{
            "appId": "66c20ac875260a035a3af7b2",
            "app": "com.alert.meserhadash",
            "androidId": "1234567890-Samsung-SM-G903M",
            "sdk": 10117,
            "platform": "android"
         }'
