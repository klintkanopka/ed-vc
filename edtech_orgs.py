import json
import requests
import os.path
import time
import pandas as pd
from tqdm import tqdm

def filterEdTechs(source_path, org_path):
    df = pd.read_csv(source_path)
    df = df[df['category_list'].str.contains('EdTech', na=False)]
    df = df[df['primary_role'].str.contains('company', na=False)]
    df.to_csv(org_path, index=False)

def createEdgeList(batch_endpoint, key, org_path, con_path):
    org_df = pd.read_csv(org_path)

    headers = {'X-Cb-User-Key': key, 'Content-Type': 'application/json'}
    reqs = {}
    req_list = []
    uuids = org_df.uuid.to_numpy()

    for uuid in uuids:
        r = {   'type': 'Organization',
                'uuid': uuid,
                'relationships': ['funding_rounds']
            }

        req_list.append(r)

    ss = []

    ss.append([
        'org_name',
        'org_permalink',
        'org_id',
        'investor_name',
        'investor_permalink',
        'investor_id',
        'investment_id',
        'money_invested_usd',
        'round_id',
        'funding_type',
        'series',
        'announced_on',
        'money_raised_usd',
        'target_money_raised_usd',
        'pre_money_valuation_usd'
        ])

    start = 0
    end = 0
   
    pbar = tqdm(total = len(req_list))

    while end < len(req_list):
        start = end
        end += 10

        reqs['requests'] = req_list[start:end]

        while True:
            try:
                resp = requests.post(
                        url = batch_endpoint,
                        headers = headers,
                        json = reqs
                        )
                resp = json.loads(resp.text)
            
            except:
                print("exception: retrying batch", (end/10))
                time.sleep(5)
                continue
            
            break
       
        for org in resp['data']['items']:
            org_id = org['uuid']
            org_name = org['properties']['name']
            org_permalink = org['properties']['permalink']
            for fr in org['relationships']['funding_rounds']['items']:
                round_id = fr['uuid']
                frp = fr['properties']
                funding_type = frp['funding_type']
                series = frp['series']
                announced_on = frp['announced_on']
                money_raised_usd = frp['money_raised_usd']
                target_money_raised_usd = frp['target_money_raised_usd']
                pre_money_valuation_usd = frp['pre_money_valuation_usd']

                if 'relationships' in fr.keys():
                    for inv in fr['relationships']['investments']:
                        investment_id = inv['uuid']
                        money_invested_usd = inv['properties']['money_invested_usd']

                        if 'relationships' in inv.keys():
                            investor = inv['relationships']['investors']
                            investor_id = investor['uuid']
                            investor_permalink = investor['properties']['permalink']
                        
                            if 'name' in investor['properties'].keys():
                                investor_name = investor['properties']['name']
                            else:
                                investor_name = 'NA'
                        
                        else:
                            investor_id = 'NA'
                            investor_name = 'NA'
                            investor_permalink = 'NA'
                
                else:
                    investor_id = 'NA'
                    investor_name = 'NA'
                    investor_permalink = 'NA'
                    investment_id = 'NA'
                    money_invested_usd = 'NA'
                
                ss.append([
                    org_name,
                    org_permalink,
                    org_id,
                    investor_name,
                    investor_permalink,
                    investor_id,
                    investment_id,
                    money_invested_usd,
                    round_id,
                    funding_type,
                    series,
                    announced_on,
                    money_raised_usd,
                    target_money_raised_usd,
                    pre_money_valuation_usd
                    ])
        pbar.update(10)

    pbar.close()

    con_df = pd.DataFrame(ss[1:], columns = ss[0])
    con_df.to_csv(con_path, index=False)

def filterVCs(source_path, con_path, inv_path):
    org_df = pd.read_csv(source_path)
    con_df = pd.read_csv(con_path)
    
    investors = con_df.investor_permalink.to_numpy()
    
    inv_df = org_df[org_df['permalink'].isin(investors)]
    inv_df.to_csv(inv_path, index=False)

def main(batch_endpoint, key_path, source_path, org_path, con_path, inv_path):
    
    with open(key_path, 'r') as key_file:
        key = key_file.read().replace('\n', '')

    if os.path.exists(org_path):
        print(org_path, 'already exists...')
    else:
        print('creating', org_path, '...')
        filterEdTechs(source_path, org_path)

    if os.path.exists(con_path):
        print(con_path, 'already exists...')
    else:
        print('creating', con_path, '...')
        createEdgeList(batch_endpoint, key, org_path, con_path)
    
    if os.path.exists(inv_path):
        print(inv_path, 'already exists...')
    else:
        print('creating', inv_path, '...')
        filterVCs(source_path, con_path, inv_path)


if __name__ == '__main__':
    main(
            'http://api.crunchbase.com/v3.1/batch',
            'key.txt',
            'data/organizations.csv', 
            'data/edtech_orgs.csv', 
            'data/edtech_cons.csv', 
            'data/edtech_invs.csv'
        )
