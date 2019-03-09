from lib.transaction import write_transactions_to_file, get_transactions_from_file

import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Consolidate all transactions from standard format into one file')
    parser.add_argument('--input_files',
                        required=True,
                        nargs="+",
                        help="space separated list of all standard exchange data you would like to consolidate")
    parser.add_argument('--export_file',
                        default='consolidated_standard_exchange.csv',
                        help='name of the file where consolidated standard exchange data will be saved')
    return parser.parse_args()


def run():
    args = parse_arguments()

    transactions = list()
    for input_file in args.input_files:
        transactions.extend(get_transactions_from_file(input_file))

    transactions.sort(key=lambda x: x.date)

    write_transactions_to_file(transactions, args.export_file)


if __name__ == '__main__':
    run()

