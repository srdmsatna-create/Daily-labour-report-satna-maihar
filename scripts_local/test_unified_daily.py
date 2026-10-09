import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts_local'/f'{name}.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class DailyTests(unittest.TestCase):
 def test_official_parser_preserves_empty_columns_and_ignores_layout(self):
  m=load('local_auto_update')
  html='<table><tr><td><table><tr><td>1</td><td>AMARPATAN</td><td>75</td><td>74</td><td>280</td><td>184</td><td></td><td>190</td></tr></table></td></tr></table>'
  row=m.parse_all_report(html)['AMARPATAN']
  self.assertEqual((row['totalGP'],row['musterGP'],row['labourAll'],row['mrAll'],row['noEkyc'],row['mrs']),(75,74,280,184,0,190))
 def test_rejected_wage_requires_all_three_years_without_duplicates(self):
  m=load('update_all_tabs')
  janpads=['AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA']
  rows=[{'fy':fy,'janpad':j} for fy in ('2024-25','2025-26','2026-27') for j in janpads]
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'data').mkdir();path=root/'data/rejected-wage-latest.json'
   def write(rr):path.write_text(json.dumps({'date':m.datetime.now(m.ZoneInfo('Asia/Kolkata')).date().isoformat(),'combined':True,'rows':rr}))
   write(rows);m.validate('rejected_wage',root)
   write(rows[:8])
   with self.assertRaises(ValueError):m.validate('rejected_wage',root)
   write(rows[:-1]+[rows[0]])
   with self.assertRaises(ValueError):m.validate('rejected_wage',root)
 def test_failed_second_step_restores_entire_group(self):
  m=load('update_all_tabs')
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'old.js').write_text('verified yesterday')
   def executor(command,root):
    if command[0]=='first':
     (root/'old.js').write_text('partial today');(root/'new.js').write_text('partial today')
    else:raise RuntimeError('official source unavailable')
   result=m.refresh_group('test',[['first'],['second']],['old.js','new.js'],root,executor,lambda *args:None)
   self.assertFalse(result['success']);self.assertEqual((root/'old.js').read_text(),'verified yesterday');self.assertFalse((root/'new.js').exists())
 def test_validator_failure_also_rolls_back(self):
  m=load('update_all_tabs')
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'report.js').write_text('good')
   def execute(command,root):(root/'report.js').write_text('bad totals')
   def validate(*args):raise ValueError('GP total mismatch')
   result=m.refresh_group('test',[['fetch']],['report.js'],root,execute,validate)
   self.assertFalse(result['success']);self.assertEqual((root/'report.js').read_text(),'good')
 def test_gp_progress_is_not_inferred_from_labour(self):
  m=load('update_gp_emuster')
  cell=lambda value:{'text':str(value),'links':[]}
  headers=['Panchayat','Maximum Expected Labour Engagement','Ongoing Works for which Muster issued','Works in Progress']
  # Active GP without today's labour must still count as active.
  tables=[[list(map(cell,headers)),list(map(cell,['GP A',0,0,1])),list(map(cell,['GP B',2,1,0]))]]
  expected={'janpad':'TEST','gps':2,'labour':2,'works':1,'progressGP':1}
  rows=m.gps_from(tables,expected)
  self.assertEqual([r['gpsProgress'] for r in rows],[1,0]);self.assertTrue(all(r['gpProgressVerified'] for r in rows))
  expected['progressGP']=2;rows=m.gps_from(tables,expected)
  self.assertTrue(all(r['gpsProgress'] is None for r in rows))
 def test_missing_progress_column_does_not_reuse_old_flag(self):
  m=load('update_gp_emuster');cell=lambda value:{'text':str(value),'links':[]}
  tables=[[list(map(cell,['Panchayat','Expected Labour Engagement','Ongoing Works for which Muster issued'])),list(map(cell,['GP A',2,1]))]]
  rows=m.gps_from(tables,{'janpad':'TEST','gps':1,'labour':2,'works':1,'progressGP':1})
  self.assertIsNone(rows[0]['gpsProgress']);self.assertFalse(rows[0]['gpProgressVerified'])

if __name__=='__main__':unittest.main()
