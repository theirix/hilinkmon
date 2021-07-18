import logging
import re
from typing import Optional

import requests
import xmltodict

logger = logging.getLogger(__name__)


class HilinkParser:
    """
    Parser for Hilink monitoring API
    """

    def __init__(self, hilink_url):
        self._hilink_url = hilink_url

    def _auth(self, session) -> Optional[dict]:
        """
        Authorize against hilink API
        """
        resp = session.get(self._hilink_url + "/api/webserver/SesTokInfo")
        if resp.status_code == 200:
            api_session = xmltodict.parse(resp.text).get("response", None)
        else:
            logger.warning(f"Bad auth request: {resp.status_code}: {resp.text}")
            return None

        auth_headers = {
            "Cookie": api_session["SesInfo"],
            "__RequestVerificationToken": api_session["TokInfo"],
        }
        return auth_headers

    def _fetch_values(self, session, headers: dict, path: str) -> Optional[dict]:
        """
        Make an authorized request to hilink API
        """
        headers["Content-Type"] = "text/xml; charset=UTF-8"
        api_url = self._hilink_url + path
        resp = session.get(api_url, headers=headers)
        if resp.status_code == 200:
            xresp = xmltodict.parse(resp.text)
            if xresp.get("response"):
                mon_data = dict(xresp["response"])
                return mon_data
        return None

    def _fetch_raw_sensors(self, session) -> dict:
        """
        Fetch raw sensors data
        """
        auth_headers = self._auth(session)
        if not auth_headers:
            return {}

        raw_sensors = {}
        endpoints = (
            "/config/dialup/config.xml",
            "/api/monitoring/status",
            "/api/net/current-plmn",
            "/api/net/cell-info",
            "/api/device/signal",
            "/api/device/information",
        )
        for endpoint in endpoints:
            res_values = self._fetch_values(session, auth_headers, endpoint)
            if res_values:
                raw_sensors.update(res_values)

        return raw_sensors

    def request(self) -> dict:
        """
        Fetch a single sensor dict
        """
        with requests.Session() as session:
            raw_sensors = self._fetch_raw_sensors(session)

            sensors = {
                key: adapted_value
                for key, value in raw_sensors.items()
                if (adapted_value := self.parse_value(key, value)) is not None
            }

            return sensors

    @staticmethod
    def parse_value(key: str, value):
        """
        Parse raw sensor value
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        value = re.sub(r"(.*)dBm$", r"\1", value)
        value = re.sub(r"(.*)dB$", r"\1", value)
        value = re.sub(r"^>=(.*)", r"\1", value)

        if key == "cellinfo":
            return str(value)

        if value.isnumeric():
            if abs(int(value)) > 0xFFFFFFFF:
                return str(value)
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
