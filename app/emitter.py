import logging
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxEmitter:
    """
    Class to emit measurements to InfluxDB
    """

    def __init__(self, url, token, org, bucket):
        self._bucket = bucket
        logger.info(f"Using {org=} and {bucket=}")

        self._client = InfluxDBClient(url=url, token=token, org=org)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def check(self) -> bool:
        """Check availability of the bucket"""
        bucket = self._client.buckets_api().find_bucket_by_name(self._bucket)
        return bool(bucket)

    def emit_sensors(self, sensors: dict):
        """Send measurement to DB"""
        self._write_api.write(
            self._bucket,
            record=[
                {
                    "measurement": "tick",
                    "tags": {"present": True},
                    "fields": sensors,
                    "time": datetime.utcnow(),
                }
            ],
        )
