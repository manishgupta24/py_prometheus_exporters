import asyncio
import logging
import subprocess
from time import sleep

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

from utils import count_greenlets, has_existing_greenlets

# Initialize Logging and print output to console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Constants
SLEEP_TIMEOUT = 3
PUSH_GATEWAY_USERNAME = "admin"
PUSH_GATEWAY_PASSWORD = "admin"
PUSH_GATEWAY_PATH = "localhost:9091"


def my_auth_handler(url, method, timeout, headers, data):
    username = PUSH_GATEWAY_USERNAME
    password = PUSH_GATEWAY_PASSWORD
    return basic_auth_handler(url, method, timeout, headers, data, username,
                              password)


async def init_prometheus_exporter_metrics():
    # Define Registry
    registry = CollectorRegistry()

    # Add metrics to registry
    # CPU Usage
    cpu_gauge = Gauge(
        'py_exporter_cpu_usage',
        'CPU Usage using Python Exporter',
        registry=registry,
        labelnames=("exporter_id", ),
        labelvalues=(1, ))
    cpu_gauge.set_to_current_time()

    # Memory Usage
    memory_gauge = Gauge(
        'py_exporter_memory_usage',
        'Memory Usage using Python Exporter',
        registry=registry)
    memory_gauge.set_to_current_time()

    # Disk Usage
    disk_gauge = Gauge(
        'py_exporter_disk_usage',
        'Disk Usage using Python Exporter',
        registry=registry)
    disk_gauge.set_to_current_time()

    return (registry, {
        "cpu_gauge": cpu_gauge,
        "memory_gauge": memory_gauge,
        "disk_gauge": disk_gauge
    })


async def cpu_usage():
    cmd = ["sh", "shell_exporters/cpu_load.sh"]
    ps = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    percentage = float(ps.stdout.decode("utf-8"))
    logger.debug("CPU Load percentage is %s" % percentage)
    return {"cpu_gauge": percentage}


async def memory_usage():
    cmd = ["sh", "shell_exporters/memory_load.sh"]
    ps = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    percentage = float(ps.stdout.decode("utf-8"))
    logger.debug("Memory Usage percentage is %s" % percentage)
    return {"memory_gauge": percentage}


async def disk_usage():
    cmd = ["sh", "shell_exporters/disk_usage.sh"]
    ps = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    percentage = float(ps.stdout.decode("utf-8"))
    logger.debug("Disk Usage percentage is %s" % percentage)
    return {"disk_gauge": percentage}


async def push_metrics(loop, registry=None, **kwargs):
    # Define list of all metric functions
    # asyncio will create a event loop to execute all function calls asynchronously
    # and will update the collector registry to reflect the latest value.
    metric_funcs = [cpu_usage, memory_usage, disk_usage]

    tasks = [loop.create_task(func()) for func in metric_funcs]
    for task in tasks:
        result = await task
        if result:
            for key, value in result.items():
                kwargs[key].set(value)

    # Push Data
    push_to_gateway(
        PUSH_GATEWAY_PATH,
        job='python_exporter_usage_metric',
        registry=registry,
        handler=my_auth_handler)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    registry, metrics_kwargs = loop.run_until_complete(
        init_prometheus_exporter_metrics())

    while True:
        loop.run_until_complete(
            push_metrics(loop, registry=registry, **metrics_kwargs))

        # Sleep for n seconds. Defined as SLEEP_TIMEOUT var
        logger.debug("Sleeping for %s seconds ..." % SLEEP_TIMEOUT)
        sleep(SLEEP_TIMEOUT)
