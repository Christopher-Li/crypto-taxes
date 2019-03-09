from lib.transaction import Transaction, get_transactions_from_file
from lib.tax_report import TaxReport

import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate tax report from consolidated standard transactions')
    parser.add_argument('--input_file',
                        required=True,
                        help="Location of consolidated standard transactions")
    parser.add_argument('--export_file',
                        default='tax_returns.csv',
                        help='name of the file where all data will be stored')
    parser.add_argument('--algorithm',
                        default="FIHO",
                        help="Choose the selection algorithm. Default is FIHO.")
    return parser.parse_args()


def run():
    args = parse_arguments()
    transactions = get_transactions_from_file(args.input_file)

    tax_report = TaxReport(transactions, args.algorithm)
    tax_report.generate_tax_report(args.export_file)


if __name__ == '__main__':
    run()

