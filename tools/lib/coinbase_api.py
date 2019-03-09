import requests


# currency_pair examples = "eth-usd", "btc-usd"
def get_historic_price(currency, date):
    # Documentation: https://developers.coinbase.com/api/v2?python#get-spot-price
    currency_pair = currency + "-usd"
    resp = requests.get("https://api.coinbase.com/v2/prices/%s/spot" % currency_pair,
                        headers=get_headers(),
                        params={"date": date})

    return resp.json()["data"]["amount"]


def is_coinbase_price_available(currency):
    if currency == "eth" or currency == "btc":
        return True
    return False


def get_headers():
    return {"CB-VERSION": "2018-03-22"}
