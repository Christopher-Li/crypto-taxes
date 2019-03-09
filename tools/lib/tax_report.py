from datetime import timedelta
from transaction import write_transactions_to_file

import collections
import sys
import heapq


class TaxReport:

    def __init__(self, transactions, algorithm):
        # currency to priority queue mapping
        self.heapq_transactions_dict = collections.defaultdict(list)
        self.short_term_proceeds = 0
        self.short_term_cost_basis = 0
        self.long_term_proceeds = 0
        self.long_term_cost_basis = 0
        self.fees = 0
        self.currency_values_cache = dict()
        self.transactions = transactions
        self.algorithm = algorithm

    def generate_tax_report(self, export_file):
        for i, transaction in enumerate(self.transactions):
            if transaction.is_taxable():
                self.resolve_taxable_transaction(transaction)
            else:
                self.add_non_taxable_transaction_to_heapq(transaction)
            sys.stdout.write("Progress: %d%% \r" % (100.0*i/len(self.transactions)))
            sys.stdout.flush()

        writer = write_transactions_to_file(self.get_remaining_transactions(), export_file)

        # print remaining data
        writer.writerow([])
        writer.writerow(["Short term proceeds", self.short_term_proceeds])
        writer.writerow(["Short term cost basis", self.short_term_cost_basis])
        writer.writerow(["Short term capital gains", self.short_term_proceeds - self.short_term_cost_basis])
        writer.writerow(["Long term proceeds", self.long_term_proceeds])
        writer.writerow(["Long term cost basis", self.long_term_cost_basis])
        writer.writerow(["Long term capital gains", self.long_term_proceeds - self.long_term_cost_basis])
        writer.writerow(["Fees paid", self.fees])

    def resolve_taxable_transaction(self, transaction):
        if transaction.currency == "usd" and transaction.transaction_type == "fee":
            self.fees += abs(transaction.amount)
            return

        while transaction.amount < 0:
            _, prev_transaction = heapq.heappop(self.heapq_transactions_dict[transaction.currency])
            self.update_capital_gains(prev_transaction, transaction)
            self.decrement_transaction_amounts(prev_transaction, transaction)

    def decrement_transaction_amounts(self, prev_transaction, transaction):
        if prev_transaction.amount + transaction.amount > 0:
            prev_transaction.amount += transaction.amount
            transaction.amount = 0
            self.add_non_taxable_transaction_to_heapq(prev_transaction)
        else:
            transaction.amount += prev_transaction.amount

    def update_capital_gains(self, prev_transaction, transaction):
        min_transaction_amount = min(prev_transaction.amount, abs(transaction.amount))
        if transaction.is_fee(): # no usd transactions at this point
            self.fees += abs(min_transaction_amount*prev_transaction.value)
        else:
            total_proceeds = min_transaction_amount * transaction.value
            cost_basis = min_transaction_amount * prev_transaction.value
            if transaction.date > prev_transaction.date + timedelta(days=365):
                self.long_term_proceeds += total_proceeds
                self.long_term_cost_basis += cost_basis
            else:
                self.short_term_proceeds += total_proceeds
                self.short_term_cost_basis += cost_basis

    def add_non_taxable_transaction_to_heapq(self, transaction):
        heapq.heappush(self.heapq_transactions_dict[transaction.currency], (-transaction.value, transaction))

    def get_remaining_transactions(self):
        remaining_transactions = list()
        for transactions in self.heapq_transactions_dict.values():
            remaining_transactions.extend([tx for key, tx in transactions])

        remaining_transactions.sort(key=lambda x: x.date)
        return remaining_transactions

    # testing
    def calculate_sum(self):
        eth_value = 0
        btc_value = 0
        for transaction in self.transactions:
            if transaction.currency == 'eth':
                eth_value += transaction.amount
            else:
                btc_value += transaction.amount
        print eth_value
        print btc_value

