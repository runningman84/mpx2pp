#!/usr/bin/env python

import csv
import re
import locale
import argparse

# required arg
parser = argparse.ArgumentParser()
parser.add_argument('in_filename')
parser.add_argument('out_filename')

args = parser.parse_args()

in_filename = args.in_filename
out_filename = args.out_filename

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

depot = "Ing-Diba"
konto = "Ing-Diba Extra"

# file = open(filename, "r")
# print(file.readlines())

# 0 -- 02.04.09;
# 1 -- ANLEIHEN KAUF  Gutschrift;
# 2 -- ;
# 3 -- ;
# 4 -- ;
# 5 -- ;
# 6 -- 2.000,00;
# 7 -- MAX Mustermann;
# 8 -- 1234567890;
# 9 -- 25010030;
# 10 -- Postbank Hannover


#header = ["Datum", "TXT", "", ""]

parsed_res = []


with open(in_filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:

        transaction_date = row[0]
        transaction_isin = None
        transaction_type  = None
        transaction_value = row[6]
        transaction_extra = None
        transaction_depot = None
        transaction_amount = None

        transaction_value_converted = locale.atof(transaction_value)

        #print(transaction_value_converted)

        m = re.search('ISIN\s*((AD|AE|AF|AG|AI|AL|AM|AO|AQ|AR|AS|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BJ|BL|BM|BN|BO|BQ|BR|BS|BT|BV|BW|BY|BZ|CA|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|CO|CR|CU|CV|CW|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EE|EG|EH|ER|ES|ET|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|IN|IO|IQ|IR|IS|IT|JE|JM|JO|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MF|MG|MH|MK|ML|MM|MN|MO|MP|MQ|MR|MS|MT|MU|MV|MW|MX|MY|MZ|NA|NC|NE|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|SS|ST|SV|SX|SY|SZ|TC|TD|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TR|TT|TV|TW|TZ|UA|UG|UM|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|YE|YT|ZA|ZM|ZW|XS)((?![A-Z]{10}\b)[A-Z0-9]{10}))', row[1])

        if m is not None:
            transaction_isin = m.group(1)

        m = re.search("Gutschrift",row[1])
        if m is not None:
            transaction_type = "Einlage"
            transaction_isin = None

        m = re.search("Sondertilgung",row[1], re.I)
        if m is not None:
            if transaction_value_converted < 0:
                transaction_type = "Entnahme"
                transaction_extra = "Kredit"

        m = re.search("Lastschrifteinzug",row[1])
        if m is not None:
            transaction_type = "Einlage"
            transaction_isin = None

        m = re.search("Wertpapierkauf",row[1])
        if m is not None:
            transaction_type = "Kauf"
            transaction_amount = 1

        m = re.search("Wertpapiergutschrift",row[1])
        if m is not None:
            transaction_type = "Verkauf"
            transaction_amount = 1

        m = re.search("Zins\/Dividende",row[1])
        if m is not None:
            transaction_type = "Dividende"

        m = re.search("Überweisung",row[1])
        if m is not None:
            if transaction_value_converted < 0 and transaction_type is None:
                transaction_type = "Entnahme"

        m = re.search("Abschluss",row[1])
        if m is not None:
            if transaction_value_converted > 0 and transaction_type is None:
                transaction_type = "Zinsen"

        m = re.search("steuer|Solidaritätszuschlag",row[1], re.I)
        if m is not None:
            if transaction_value_converted < 0 and transaction_type is None:
                transaction_type = "Steuern"
            elif transaction_value_converted >= 0 and transaction_type is None:
                transaction_type = "Steuerrückerstattung"

        m = re.search('([0-9]{2}\/[0-9]{2})',row[1])
        if m is not None:
            transaction_extra = "Anleihe"


        if transaction_value_converted == 0 and transaction_type is None:
                continue

        if transaction_type is None:
            print(row)

        if transaction_isin is not None:
            transaction_depot = depot

        dict = {'Datum': transaction_date,
        'Typ': transaction_type,
        'ISIN': transaction_isin,
        'WKN': transaction_isin,
        'Wert': transaction_value,
        'Zusatz': transaction_extra,
        'Betreff': row[1],
        'Depot': transaction_depot,
        'Konto': konto,
        'Stück': transaction_amount
        }

        parsed_res.append(dict)
        print(dict)
        line_count = line_count + 1

    print(f'Processed {line_count} lines.')

with open(out_filename, mode='w') as out_file:
    fieldnames = parsed_res[0].keys()
    writer = csv.DictWriter(out_file, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for dataset in parsed_res:
        writer.writerow(dataset)