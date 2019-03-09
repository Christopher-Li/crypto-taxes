from lib.exchange_converter import \
    GeminiExchangeConverter, \
    GdaxExchangeConverter, \
    CoinbaseExchangeConverter, \
    BinanceExchangeConverter
from lib.transaction import write_transactions_to_file
from lib import coinbase_api
from lib.value_adapter import ValueAdapter

import argparse
import csv


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert all exchange data into a standard format')
    parser.add_argument('--exchange',
                        required=True,
                        help='Name of exchange whose data you are inputting. i.e. Gemini, Gdax, or Coinbase')
    parser.add_argument('--input_file',
                        required=True,
                        help="path to trade data")
    parser.add_argument('--export_file',
                        default='standard_transactions.csv',
                        help='name of the file where data will be saved. default: standard_transactions.csv')
    return parser.parse_args()


def run():
    args = parse_arguments()

    # initialize variables
    transactions = list()

    # standard data format:
    # date, currency, transaction type(buy, sell, deposit, withdraw, fee)
    with open(args.input_file, 'rb') as csv_file:
        csv_reader_data = csv.reader(csv_file)

        if args.exchange.lower() == "gdax":
            exchange_converter = GdaxExchangeConverter(csv_reader_data)
        elif args.exchange.lower() == "gemini":
            exchange_converter = GeminiExchangeConverter(csv_reader_data)
        elif args.exchange.lower() == "coinbase":
            exchange_converter = CoinbaseExchangeConverter(csv_reader_data)
        elif args.exchange.lower() == "binance":
            exchange_converter = BinanceExchangeConverter(csv_reader_data)
        else:
            raise Exception("%s is not a valid exchange" % args.exchange)

        transactions = exchange_converter.get_standard_transactions()

    value_adapter = ValueAdapter()
    for transaction in transactions:
        value_adapter.set_transaction_value(transaction)

    write_transactions_to_file(transactions, args.export_file)


if __name__ == '__main__':
    run()

