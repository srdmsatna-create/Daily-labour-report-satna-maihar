"""Refresh Planner daily-progress status counts from the two All Planning exports."""
import argparse,csv,json,re
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ALIASES={('SOHAWAL','KHADOURA'):'KHADAURA',('RAMNAGAR','NEWDEVRAJNAGAR'):'NEWDEORAJNAGAR'}

def key(value):
    return re.sub('[^A-Z0-9]','',str(value).upper())

def block_name(value):
    value='Sohawal' if key(value)=='SATNA' else str(value).strip().title()
    return 'Rampur baghelan' if key(value)=='RAMPURBAGHELAN' else value

def main(files,source_date):
    master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig',newline='')))
    mapping={}
    for row in master:
        for gp in (row['Gram_Panchayat'],row['GP_20Sep_Name']):
            mapping[(key(row['Janpad']),key(gp))]=row
    counts=defaultdict(lambda:[0,0,0,0])
    source_rows=0
    for path in files:
        for _,row in pd.read_excel(path).iterrows():
            source_rows+=1
            block=block_name(row['Block'])
            gp_key=(key(block),key(row['Panchayat']))
            gp_key=(gp_key[0],ALIASES.get(gp_key,gp_key[1]))
            mapped=mapping.get(gp_key)
            if not mapped:
                raise ValueError(f"GP mapping missing: {block}/{row['Panchayat']}")
            district='Maihar' if block in ('Amarpatan','Maihar','Ramnagar') else 'Satna'
            values=counts[(district,block,mapped['Sub_Engineer'])]
            values[0]+=1
            status=str(row['Planning Status']).strip().lower()
            values[1]+=status=='approved by ae'
            values[2]+=status=='reviewed by sa'
            values[3]+=status=='rejected'
    if source_rows!=2569:
        raise ValueError(f'Expected 2,569 All Planning rows; got {source_rows:,}')
    target=ROOT/'planner-daily-progress-data.js'
    payload=json.loads(target.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    for row in payload['rows']:
        group=(row['district'],row['janpad'],row['engineer'])
        if group not in counts and row['now'][1]:
            raise ValueError('Non-empty daily-progress group missing from source: '+str(group))
        valid,approved,reviewed,rejected=counts.get(group,[0,0,0,0])
        row['now'][1:5]=[valid,approved,reviewed,rejected]
    payload['currentDate']=source_date.strftime('%d-%m-%Y')
    payload['sourceNote']=f"स्रोत: 27-10-2026 baseline और {payload['currentDate']} All_Planning_Summary। आज की दोनों Excel में सतना–मैहर की 2,569 मान्य पंक्तियाँ एक बार गिनी गई हैं।"
    target.write_text('window.PLANNER_DAILY_PROGRESS='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps({'rows':source_rows,'approved':sum(v[1] for v in counts.values()),'reviewed':sum(v[2] for v in counts.values()),'rejected':sum(v[3] for v in counts.values())},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('files',nargs='+',type=Path)
    parser.add_argument('--date',type=date.fromisoformat,required=True)
    args=parser.parse_args()
    main(args.files,args.date)
