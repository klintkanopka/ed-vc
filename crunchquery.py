#!/usr/bin/env python3

import json
import urllib.request
import pandas as pd

def main(file_path):
    cb = CrunchbaseQuery()
    ss = []
    headers = ['investor name',
        'investment permalink',
        'investment uuid',
        'investment founded_on',
        'money_invested',
        'investment date',
        'funding type',
        'funding round',
        'funding round uuid',
        'funding round announcement date',
        'total money raised',
        'investment name',
        'investment description',
        'investment url']
    ss.append(headers)

    with open(file_path) as fp:
        for line in fp:
            print(line)
            line = line.replace("\n", "")
            response = cb.requestInvestments(line)
            ss = cb.formatInvestments(response, ss)
    df = pd.DataFrame(ss[1:], columns=ss[0])
    df.to_csv('ed-test.csv')

class CrunchbaseQuery:
    def __init__(self, key_path = 'key.txt'):
        with open(key_path, 'r') as key_file:
            self.key = key_file.read().replace('\n', '')

    def request(self, org, relationships=['investments']):
        url = 'https://api.crunchbase.com/v3.1/organizations/' + org + '?relationships=' + ','.join(relationships) + '&user_key=' + self.key
        return json.load(urllib.request.urlopen(url))

    def requestInvestments(self, org):
        url = 'https://api.crunchbase.com/v3.1/organizations/' + org + '/investments?relationships=investments&user_key=' + self.key
        print(url)
        return (org, json.load(urllib.request.urlopen(url)))

    def formatInvestments(self, response, spreadsheet):
        for inv in response[1]['data']['items']:
            s = []
            # investor name
            s.append(response[0])
            # investment permalink
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['properties']['permalink'])
            # investment uuid
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['uuid'])
            # investment founded_on
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['properties']['founded_on'])
            # money_invested
            s.append(inv['properties']['money_invested'])
            # investment date
            s.append(inv['properties']['announced_on'])
            # funding type
            s.append(inv['relationships']['funding_round']['properties']['funding_type'])
            # funding round
            s.append(inv['relationships']['funding_round']['properties']['series'])
            # funding round uuid
            s.append(inv['relationships']['funding_round']['properties']['permalink'])
            # funding round announcement date
            s.append(inv['relationships']['funding_round']['properties']['announced_on'])
            # total money raised
            s.append(inv['relationships']['funding_round']['properties']['money_raised'])
            # investment name
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['properties']['name'])
            # investment description
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['properties']['description'])
            # investment url
            s.append(inv['relationships']['funding_round']['relationships']['funded_organization']['properties']['homepage_url'])
            spreadsheet.append(s)
        
        return(spreadsheet)


if __name__ == '__main__':
    main('vc-ed.txt')
