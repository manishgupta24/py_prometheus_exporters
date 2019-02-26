from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler
from random import randint
from time import sleep

SLEEP_TIMEOUT = 1
PUSH_GATEWAY_USERNAME = "admin"
PUSH_GATEWAY_PASSWORD = "admin"
PUSH_GATEWAY_PATH = 'localhost:9091'


def my_auth_handler(url, method, timeout, headers, data):
    username = PUSH_GATEWAY_USERNAME
    password = PUSH_GATEWAY_PASSWORD
    return basic_auth_handler(url, method, timeout, headers, data, username,
                              password)


def cpu_usage():
    return float(randint(0, 100))


if __name__ == "__main__":
    registry = CollectorRegistry()
    gauge = Gauge(
        'py_exporter_cpu_usage',
        'CPU Usage using Python Exporter',
        registry=registry)
    gauge.set_to_current_time()
    while True:
        cpu_usage_value = cpu_usage()
        gauge.set_function(cpu_usage)
        push_to_gateway(
            PUSH_GATEWAY_PATH,
            job='python_exporter_usage_metric',
            registry=registry,
            handler=my_auth_handler)
        print("CPU Usage --> %s" % cpu_usage_value)
        print("Sleeping for %s seconds ..." % SLEEP_TIMEOUT)
        sleep(SLEEP_TIMEOUT)
