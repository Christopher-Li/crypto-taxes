# crypto-taxes

I've been able to use these to calculate my crypto tax returns for the previous few years.

## Disclaimer

I am not a tax expert, any tax return produced by this algorithm could be faulty.

## Instructions

- Step 1: Download csv of all transactions from cryptocurrency exchanges
- Step 2: Convert to standard transaction csv format
  - Use [tools/convert\_to\_standard\_transactions.py](#toolsconvert_to_standard_transactionpy)
- Step 3: Consolidate all standard csv transactions.
  - If you have trades from previous years you would like to include, prepend the previous cost basis transactions to the consolidated file
  - Use [tools/consolidate\_standard\_transactions.py](#toolsconsolidate_standard_transactionspy)
- Step 4: Generate a tax report
  - Use [tools/generate\_tax\_report.py](#toolsgenerate_tax_reportpy)
  
  
## Tools

### tools/convert\_to\_standard\_transactions.py
Converts exchange csv data from the exchange to a standard format for the crypto-taxes to calculate.

Supports the following flags:
- `--input_file`: path to the input file
- `--export_file`: path to the created file
- `--exchange`: name of the cryptocurrency exchange. Only supports Gemini, Gdax, and coinbase

### tools/consolidate\_standard\_transactions.py
Consolidates all standard formated transaction files into one file with all transactions. If you only have on standard formatted transaction file, then your input_file will match your export_file.

Supports the following flags:
- `--input_files`: space delimited list of paths to the input files
- `--export_file`: path to the created file

### tools/generate\_tax\_report.py
Consolidates transaction file to all remaining cost basis and dates of purchases providing short term and long term capital gains.
Remaining purchases should be prepended to the `consolidated_standard_transactions.csv` for the following year.
Relies on FIFO algorithm to determine which cost basis to sell first.

Due to rounding errors from the exchange (Cryptocurriencies can divide more granuarly than the exchanges usually provide the data), this code may fail attempting to sell .00001 of BTC/ETH/insert random cryptocurrency that you down own.
I tend to resolve this error by just adjusting the amounts being sold by the minute fraction that usually amounts to less than $1.

Supports the following flags:
- `--input_file`: path to the input file
- `--export_file`: path to the created file
