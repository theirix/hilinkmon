import logging
import os
import sys
import time

from .emitter import InfluxEmitter
from .hilink_parser import HilinkParser
from .stat import InfluxStat

logger = logging.getLogger(__name__)


class Monitor:
    """
    Monitors Hilink API to InfluxDB time-series database
    """

    def __init__(
        self,
        hilink_parser: HilinkParser,
        emitter: InfluxEmitter,
        stat: InfluxStat,
        period: float,
    ):
        self._hilink_parser = hilink_parser
        self._emitter = emitter
        self._stat = stat
        self._period = period

    def _tick(self):
        logger.info("Tick")
        try:
            sensors = self._hilink_parser.request()
            logger.info(f"Got {len(sensors)} measurements")
            if sensors:
                logger.debug(sensors)
                self._emitter.emit_sensors(sensors)
                logger.info("Emitting done")
            else:
                logger.warning("No data to emit")
            logger.info(
                "Averages:"
                f"RSSI={self._stat.avg_rssi():.1f}, "
                f"SINR={self._stat.avg_sinr():.1f}"
            )
        except Exception as ex:  # pylint: disable=broad-except
            logger.error(f"Error at tick: {ex}", exc_info=ex)

    def run(self):
        """Infinite read-write loop"""
        try:
            while True:
                self._tick()
                time.sleep(self._period)
        except KeyboardInterrupt:
            logging.info("Exiting...")
        except Exception as ex:  # pylint: disable=broad-except
            logging.exception("Generic error", exc_info=ex)


def main_loop():
    """Entry point"""
    logging.basicConfig(
        stream=sys.stdout,
        level="DEBUG",
        format="[%(asctime)s] %(name)s[%(process)d] %(levelname)s -- %(message)s",
    )
    logger.info("Starting app")

    url = os.environ["INFLUXDB_URL"]
    token = os.environ["INFLUXDB_TOKEN"]
    org = os.environ["INFLUXDB_ORG"]
    bucket = os.environ["INFLUXDB_BUCKET"]
    hilink_url = os.environ["HILINK_URL"]

    emitter = InfluxEmitter(url, token, org, bucket)
    if not emitter.check():
        logging.error("Bucket does not exist")
        return

    stat = InfluxStat(url, token, org, bucket)
    hilink_parser = HilinkParser(hilink_url)

    monitor = Monitor(hilink_parser, emitter, stat, period=3)
    monitor.run()

    logging.info("Done")
