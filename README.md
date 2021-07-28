# hilinkmon

A simple monitoring application for HiLink LTE modems.

A HiLink modem has a status webpage but does not provide any historical data or analytics. This application  continuously fetches data from various diagnostic  API and saves metrics to the InfluxDB time-series database.

The repository also contains a pre-configured dashboard for a quick checkup of signal strength and quality (RSSI, RSRQ, SINR, CQI)


## How to run


Create a docker volume for InfluxDB data:

    docker volume create hilinkmon-influxdb-data

Build and run containers:

    docker-compose build

Now `influxdb` container should start with a preconfigured InfluxDB instance. 
Retrieve a default auth token from InfluxDB:

    docker-compose exec influxdb influx auth list --user user --hide-headers | cut -f 3

Configure `app` container to use this token using the `.env` file.
Assume the HiLink modem is available at 'http://192.168.8.1'.

    INFLUXDB_TOKEN=<base64 secret from the previous command>
    HILINK_URL=http://192.168.8.1

Rerun containers:

    docker-compose restart app

## Using the monitor

To explore data access the InfluxDB UI via 'http://localhost:8086'.
Load the preconfigured dashboard from `data/dashboard.json` file.

The monitor also prints averaged RSSI and CQI values to the standard output.
