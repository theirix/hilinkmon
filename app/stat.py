import logging
from typing import Optional

from influxdb_client import InfluxDBClient

logger = logging.getLogger(__name__)


class InfluxStat:
    """
    Class to gather simple stats from InfluxDB
    """

    def __init__(self, url, token, org, bucket):
        self._bucket = bucket
        logger.info(f"Using {org=} and {bucket=}")

        self._client = InfluxDBClient(url=url, token=token, org=org)
        self._query_api = self._client.query_api()

    def _avg_value(self, field_name) -> Optional[float]:
        """Gather aggregate for"""
        query = """
        from(bucket:"{}")
        |> range(start: -1d)
        |> filter(fn: (r) =>
            r._measurement == "tick" and
            r._field == "{}"
        )
        |> timedMovingAverage(
            every: 5m,
            period: 30m
        )
        |> top(n:1, columns:["_time"])
        """.format(
            self._bucket, field_name
        )

        result = self._query_api.query(query)

        table = result[0]
        if table.records:
            record = table.records[0]
            if record:
                return record.get_value()

        return None

    def avg_rssi(self) -> Optional[float]:
        """Gather avg RSSI"""
        return self._avg_value("rssi")

    def avg_sinr(self) -> Optional[float]:
        """Gather avg SINR"""
        return self._avg_value("sinr")
