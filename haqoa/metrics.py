from os import getenv

from prometheus_client import Counter, Gauge, start_http_server


received = Counter(
    'haqoa_received_alerts_total',
    'Number of alerts received',
    labelnames=['mqtt_host'],
)
processed = Counter(
    'haqoa_processed_alerts_total',
    'Number of alerts processed',
    labelnames=['mqtt_host'],
)
skipped = Counter(
    'haqoa_skipped_alerts_total',
    'Number of alerts skipped due to target filter',
    labelnames=['mqtt_host'],
)
delay = Gauge(
    'haqoa_delay_seconds',
    'Time delay between alert generation and notification processing',
    labelnames=['mqtt_host'],
)
client_info = Gauge(
    'haqoa_client_info',
    'Client information',
    labelnames=['token', 'auth', 'mqtt_host'],
)
target_area = Gauge(
    'haqoa_target_area',
    'Target areas registered for alerts',
    labelnames=['area_id'],
)


def expose():
    port = int(getenv('METRICS_PORT', '9100'))
    start_http_server(port)
