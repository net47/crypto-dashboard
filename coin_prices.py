import influxdb_client
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
from influxdb_client.client.write_api import SYNCHRONOUS


"""
Enter your InfluxDB settings
"""
influx_url = "http://1.2.3.4:8086"
influx_token = "xxxxxxxxxxxxxxxxxxx"
influx_org = "XYZ"
influx_client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = influx_client.query_api()
write_api = influx_client.write_api(write_options=SYNCHRONOUS)


"""
Get the price per coin using 
- the free CoinGecko API (see https://www.coingecko.com/en/api/documentation)
    Token List: https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?usp=sharing
- the unofficial Python wrapper (see https://github.com/man-c/pycoingecko)
"""
def get_price(name):
    raw = cg.get_price(ids=name, vs_currencies='eur')
    price = raw[name]["eur"]
    return float(price)


"""
Function to write the coin price to the respective InfluxDB bucket
"""
def write_data(name, symbol):
    payload = influxdb_client.Point("price_" + symbol).field("value", get_price(name))
    write_api.write(bucket="price_" + symbol, org=influx_org, record=payload)


"""
main execution
"""
def main():
    write_data("bitcoin", "btc")
    write_data("defichain", "dfi")
    write_data("litecoin", "ltc")

if __name__ == "__main__":
    main()