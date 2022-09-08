import requests, json
from forex_python.bitcoin import BtcConverter
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import urllib3
from cryptotools import Xpub

# disable HTTPS InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Enter your InfluxDB settings
"""
influx_url = "http://1.2.3.4:8086"
influx_token = "xxxxxxxxxxxxxxxxxxx"
influx_org = "XYZ"
influx_bucket = "portfolio_value"
influx_client = influxdb_client.InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = influx_client.query_api()
write_api = influx_client.write_api(write_options=SYNCHRONOUS)


"""
Use the RapidAPI free subscription to simply convert USD to EUR
"""
def convert_USD_to_EUR(value_usd):
    url = "https://currency-converter5.p.rapidapi.com/currency/convert"
    querystring = {"format":"json","from":"USD","to":"EUR","amount":value_usd}
    headers = {
        "X-RapidAPI-Key": "xxxxxxxxxxxxxxxxxxxxxxx",
        "X-RapidAPI-Host": "currency-converter5.p.rapidapi.com"
    }
    r = requests.request("GET", url, headers=headers, params=querystring)
    raw = r.json()
    value_eur = raw['rates']['EUR']['rate_for_amount']
    return value_eur


"""
Example 01: use an xpub string to get the first 50 Bitcoin addresses and their respective values
"""
def getValue_BTC(xpub):
    """
    1.) Decode xPub and get all used addresses (see https://bitcoin.stackexchange.com/a/109985)
    2.) Get the balance (in sats) of each address and sum it up
    3.) Convert it to BTC, then to EUR (see https://forex-python.readthedocs.io/en/latest/usage.html#bitcoin-prices)
    """
    key = Xpub.decode(xpub)
    addresses = []
    amount_addresses = range(50) # extend this if you already use more than 50 addresses
    for n in amount_addresses:
        pubkey = key/0/n
        addresses.append(pubkey.address('P2WPKH'))
    sats = []
    for n in amount_addresses:
        r = requests.get('https://mempool.space/api/address/' + addresses[n], verify=False)
        """
        added try-catch because it's sometimes returning an empty response
        """
        try:
            raw = r.json()
            if raw['chain_stats']['funded_txo_sum'] != 0:
                sats.append(raw['chain_stats']['funded_txo_sum'])
        except:
            pass
    balance_btc = float(sum(sats) * 0.00000001)
    b = BtcConverter()
    balance_eur = b.convert_btc_to_cur(balance_btc, 'EUR')
    return float(balance_eur)


"""
Example 02: get the value of your DeFiChain light wallet using DeFiChain-Income
"""
def getValue_DFI_LightWallet(address):
    """
    1.) Get the total value of the DFI address (incl. LM and wallet balance) from DeFiChain-Income
    2.) Convert it to EUR
    """
    r = requests.get('https://next.graphql.defichain-income.com/income/' + address, verify=False)
    out = r.json()
    total_value_usd = out['totalValue']
    total_value_eur = convert_USD_to_EUR(total_value_usd)
    return total_value_eur


"""
Function to 
1.) get the latest coin price from the respective InfluxDB bucket
2.) load the amount of coins from the input JSON file and
3.) multiply it with the coin price
"""
def getValueInfluxBucket(input_file, bucket_name):
    query = ' from(bucket:"' + bucket_name + '")\
    |> range(start: 0, stop: now())\
    |> filter(fn:(r) => r._measurement == "' + bucket_name + '")\
    |> filter(fn:(r) => r._field == "value" ) \
    |> last(column: "_time") '

    result = query_api.query(query=query)
    for table in result:
        for record in table.records:
            latest_price = record.get_value()

    f = open(input_file)
    data = json.load(f)
    try:
        sum = float(latest_price) * float(data["amount"])
        return float(sum)
    except Exception as e:
        print(repr(e))
        return float(0)

"""
main execution
"""
def main():
    btc = getValue_BTC("zpubXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    dfi_lightwallet = getValue_DFI_LightWallet("df1XXXXXXXXXXXXXXXXXXXXXXXXXX")
    ltc = getValueInfluxBucket("_litecoin.json", "price_ltc")

    sum = float(btc) + float(dfi_lightwallet) + float(ltc)

    p = influxdb_client.Point(influx_bucket).field("value", sum)
    write_api.write(bucket=influx_bucket, org=influx_org, record=p)

if __name__ == "__main__":
    main()