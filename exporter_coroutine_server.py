import asyncio
import json
import logging
import subprocess

from prometheus_client import Gauge, start_http_server, MetricsHandler

# Initialize Logging and print output to console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Define CONSTANTS
PORT_NUM = 45678
SLEEP_TIMEOUT = 3

# Define Metrics
cpu_gauge = Gauge('py_exporter_cpu_usage', 'CPU Usage using Python Exporter')
memory_gauge = Gauge('py_exporter_memory_usage',
                     'Memory Usage using Python Exporter')
disk_gauge = Gauge('py_exporter_disk_usage',
                   'Disk Usage using Python Exporter')

METRICS_MAP = {
    "cpu_gauge": cpu_gauge,
    "memory_gauge": memory_gauge,
    "disk_gauge": disk_gauge
}


def metrics_exporter():
    cmd = ["sh", "shell_exporters/exporter.sh"]
    ps = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    metrics = json.loads(ps.stdout.decode("utf-8"))
    logger.debug("METRICS: %s" % metrics)
    return metrics


async def compute_rate():
    """Increases or decreases a rate based on a random delta value
    which varies from "delta_min" to "delta_max".
    :name: task_id
    :rate: initial rate value
    :delta_min: lowest delta variation
    :delta_max: highest delta variation
    """
    while True:
        metrics = metrics_exporter()
        for key, value in metrics.items():
            METRICS_MAP[key].set(value)
        logger.debug("Sleeping for %s seconds ..." % SLEEP_TIMEOUT)
        await asyncio.sleep(SLEEP_TIMEOUT)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Start up the server to expose metrics.
    start_http_server(PORT_NUM)
    loop.create_task(compute_rate())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
