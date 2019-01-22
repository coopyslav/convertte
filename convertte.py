import argparse
import urllib.request
import xml.etree.ElementTree as ET
import json

parser = argparse.ArgumentParser()
parser.add_argument("--amount", help="how much to convert", type=float)
parser.add_argument("--input_currency", help="converting from", type=str)
parser.add_argument("--output_currency", help="converting to", type=str, default='all')
parser.parse_args()
args = parser.parse_args()
amount = float()
srcCurr = str()
tgtCurr = str()
if args.amount:
    amount = args.amount
if args.input_currency:
    srcCurr = args.input_currency
if args.output_currency:
    tgtCurr = args.output_currency

#rates from European Central Bank
if urllib.request.urlopen("https://www.ecb.europa.eu/").getcode() == 200:
    url = ("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")
    ratesXML = urllib.request.urlopen(url)
    tree = ET.parse(ratesXML)
    root = tree.getroot()
    tree.write('eurofxref-daily.xml')

#symbols and codes
currencies = {'€': 'EUR', '$': 'USD', '¥': 'JPY', 'лв.': 'BGN', 'Kč': 'CZK', 'Dkr': 'DKK', '£': 'GBP', 'Ft': 'HUF', 'zł': 'PLN', 'RON': 'RON', 'kr': 'SEK', 'CHF': 'CHF', 'Íkr': 'ISK', 'Nkr': 'NOK', 'kn': 'HRK', '₽': 'RUB', '₺': 'TRY', 'AU$': 'AUD', 'R$': 'BRL', 'CA$': 'CAD', 'RMB': 'CNY', 'HK$': 'HKD', 'Rp': 'IDR', '₪': 'ILS', '₹': 'INR', '₩': 'KRW', 'MEX$': 'MXN', 'RM': 'MYR', 'NZ$': 'NZD', '₱': 'PHP', 'S$': 'SGD', '฿': 'THB', 'R': 'ZAR'}

#symbol to code
if srcCurr in currencies.keys():
    for symbol in currencies.keys():
        if srcCurr == symbol:
            srcCurr = currencies[symbol]
            break

if tgtCurr in currencies.keys():
    for symbol in currencies.keys():
        if tgtCurr == symbol:
            tgtCurr = currencies[symbol]
            break


#read the XML to Dict
actualRates = {'EUR': 1}
tree = ET.parse('eurofxref-daily.xml')
root = tree.getroot()
for elem in root:  
    for subEl1 in elem:
        for subEl2 in subEl1:
            actualRates[subEl2.attrib['currency']] = float(subEl2.attrib['rate'])

#print(actualRates)

#list of tgt currencies
convertTo = []
if tgtCurr == 'all':
    for code in list(currencies.values()):
        convertTo.append(code)
else:
    convertTo.append(tgtCurr)

#convert
def convert(curr, amount, turner):
    conVerted = float()
    conVerted = amount * (actualRates[curr] ** turner)
    return conVerted

#obracecka
midEUR = float()
outToJSON = {}
for conToCurr in convertTo:
    if srcCurr == 'EUR' and conToCurr != 'EUR':
        outToJSON[conToCurr] = round(convert(conToCurr, amount, 1), 2)
    elif srcCurr != 'EUR' and conToCurr == 'EUR':
        outToJSON[conToCurr] = round(convert(srcCurr, amount, -1), 2)
    elif srcCurr == conToCurr:
        #outToJSON[conToCurr] = amount
        continue
    elif srcCurr != 'EUR' and conToCurr != 'EUR':
        midEUR = convert(srcCurr, amount, -1)
        outToJSON[conToCurr] = round(convert(conToCurr, midEUR , 1), 2)

#push to JSON
inToJSON = {}
inToJSON["amount"] = amount
inToJSON["currency"] = srcCurr

toJSON = {}
toJSON["input"] = inToJSON
toJSON["output"] = outToJSON

with open('output.json', 'w') as JSON:
    json.dump(toJSON, JSON)