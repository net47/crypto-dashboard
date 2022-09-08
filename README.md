# crypto coin dashboard

How to setup a crypto currency dashboard using 

* quick-and-dirty Python code for data fetching, normalization and processing
* InfluxDB as database
* Grafana as visualization

## requirements (on the same or on different hosts)

* Python 3
* a functionality to regularly run the Python script(s), like ```cron``` on Linux or ```SCHTASKS``` / ```TaskSceduler``` on Windows
* [InfluxDB](https://www.influxdata.com/products/influxdb-overview/) (recommended version: 2) instance
* [Grafana](https://grafana.com/) instance

Python 3 [pip](https://docs.python.org/3/installing/index.html) packages:

* [influxdb-client](https://pypi.org/project/influxdb-client/)
* [pycoingecko](https://pypi.org/project/pycoingecko/)
* [forex-python](https://pypi.org/project/forex-python/)
* [cryptotools](https://github.com/mcdallas/cryptotools)

Setup of these instances and functions are not covered here, please use the official documentation!

## file contents and setup

### InfluxDB

Install InfluxDB on the desired host and make sure to have the desired buckets:

* ```portfolio_value``` for the whole portfolio value
* ```price_XYZ``` --> for example, ```price_btc``` for Bitcoin

Note your Influx organization and API token, instructions here: [https://docs.influxdata.com/influxdb/cloud/security/tokens/create-token/](https://docs.influxdata.com/influxdb/cloud/security/tokens/create-token/)

### coin_prices.py

This script is used to fetch the desired coin prices using the free CoinGecko API and save it in InfluxDB. Off course, this is highly dependant what coins you own, adapt it as you wish. 

Run this script peridically (e.g. every 30 minutes). 

## portfolio_value.py

This script is used to sum everything up and get a total portfolio value in the end. 

Run this script peridically (e.g. every 65 minutes). 

### Grafana

You can use the following example query for a total portfolio value "Time series" chart:

```
from(bucket: "portfolio_value")
  |> range(start: v.timeRangeStart, stop:v.timeRangeStop)
  |> aggregateWindow(every: v.windowPeriod, fn: mean)
```

![total portfolio value chart](tpv.jpg)

