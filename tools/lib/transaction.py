from datetime import datetime

import csv


class Transaction:
    VALID_TRANSACTION_TYPES = ["trade", "transfer", "fee"]
    VALID_DATE_FORMATS = ["%Y-%m-%d %H:%M:%S", "%m/%d/%y  %H:%M"]

    def __init__(self, date, transaction_type, currency, amount, value=""):
        if transaction_type.lower() not in self.VALID_TRANSACTION_TYPES:
            raise Exception("%s is not a valid transaction type" % transaction_type)
        # example: "10/14/2017  11:13:57 PM"
        if type(date) is str:
            for fmt in self.VALID_DATE_FORMATS:
                try:
                    date = datetime.strptime(date, fmt)
                    break
                except ValueError:
                    continue
            if type(date) is str:
                raise Exception("None of the datetime formats were valid")

        self.date = date
        self.transaction_type = transaction_type.lower()
        self.currency = currency.lower()
        self.amount = float(amount)
        self.value = abs(float(value)) if value else value

    @staticmethod
    def get_header_row():
        return ["Date", "Transaction Type", "Currency", "Amount", "Value"]

    def is_taxable(self):
        return self.amount <= 0 or self.transaction_type == "fee"

    def is_fee(self):
        return self.transaction_type == "fee"

    def get_coinbase_date(self):
        return datetime.strftime(self.date, "%Y-%m-%d")

    def get_row(self):
        return [self.date, self.transaction_type, self.currency, self.amount, self.value]


def get_transactions_from_file(file_name):
    transactions = list()
    with open(file_name, 'rb') as csv_file:
        csv_standard_exchange_transactions = csv.reader(csv_file)
        csv_standard_exchange_transactions.next()

        for row in csv_standard_exchange_transactions:
            transactions.append(Transaction(*row))

    return transactions


def write_transactions_to_file(transactions, file_name):
    writer = csv.writer(open(file_name, 'w'))
    writer.writerow(Transaction.get_header_row())
    for transaction in transactions:
        writer.writerow(transaction.get_row())
    return writer
