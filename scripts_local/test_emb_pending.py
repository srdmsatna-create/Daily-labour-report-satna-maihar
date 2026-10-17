import unittest
from unittest.mock import patch
import update_emb_pending as m

class ZeroAttendanceTests(unittest.TestCase):
 def test_headers_and_column_numbers(self):
  for header in ('Muster Roll No.', 'e-Muster Roll Number', 'MR No.', 'E-MR No.', 'Muster Roll No.\n'):
   source=f'<table><tr><th>Sl.</th><th>Work</th><th>{header}</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>1</td><td>Road (1712001001/WC/99)</td><td>12345</td></tr></table>'
   self.assertEqual(m.zero_mrs(m.rows(source),1),{('1712001001/WC/99','12345')})
 def test_mismatch_is_not_published(self):
  with self.assertRaisesRegex(ValueError,'expected=2; observed=\\[1\\]'):
   m.zero_mrs(m.rows('<tr><th>Sl.</th><th>Work</th><th>MR No.</th></tr><tr><td>1</td><td>1712001001/WC/99</td><td>123</td></tr>'),2)
 def test_unknown_header_is_rejected(self):
  with self.assertRaises(ValueError):m.zero_mrs(m.rows('<tr><th>Sl.</th><th>Other No.</th></tr><tr><td>1</td><td>123</td></tr>'),1)

 def test_two_works_three_mrs_from_daily_failure(self):
  source='<tr><th>S No.</th><th>Project Name with code</th><th>E-MR No.</th></tr>'
  for serial,code,mr in [(1,'1712008032/IF/22012035528718','2038'),(2,'1712008032/IF/22012035609621','278'),(3,'1712008032/IF/22012035609621','850')]:
   source+=f'<tr><td>{serial}</td><td>Work ({code})</td><td>{mr}</td></tr>'
  self.assertEqual(len(m.zero_mrs(m.rows(source),2)),3)
  with self.assertRaises(ValueError):m.zero_mrs(m.rows(source),4)
  with self.assertRaises(ValueError):m.zero_mrs(m.rows(source.replace('<td>3</td>','<td>4</td>')),2)

 def test_same_mr_on_other_work_is_not_excluded(self):
  source='<tr><td>1</td><td>1712001001/WC/99</td><td>Road</td><td>123</td><td>01/10/2026</td><td></td></tr>'
  from datetime import date
  details,_=m.pending_rows(m.rows(source),'SATNA','GP',{('SATNA','GP','1712001001/WC/88','123')},date(2026,10,17))
  self.assertEqual(len(details),1)

 def test_refreshes_summary_before_retry(self):
  parent='<tr><td>1</td><td>AHIRGAON</td><td>0</td><td>0</td><td>0</td><td><a href="/detail">1</a></td><td>0</td><td>0</td><td>0</td><td>0</td></tr>'
  root=object()
  bad=m.rows('<tr><th>Sl.</th><th>MR No.</th></tr>')
  good=m.rows('<tr><th>Sl.</th><th>Work</th><th>MR No.</th></tr><tr><td>1</td><td>1712001001/WC/99</td><td>123</td></tr>')
  calls=[]
  def get(url):
   calls.append(url)
   if url==m.R42_URL:return root,'https://example.test/root'
   if url=='https://example.test/parent':return m.rows(parent),'https://example.test/parent'
   return (bad if calls.count(url)==1 else good),url
  with patch.object(m,'get',side_effect=get),patch.object(m,'block_links',return_value={'AMARPATAN':'https://example.test/parent'}),patch.object(m.time,'sleep'):
   result,_=m.load_zero_attendance()
  self.assertEqual(result,{('AMARPATAN','AHIRGAON','1712001001/WC/99','123')})
  self.assertEqual(calls.count('https://example.test/parent'),2)

if __name__=='__main__':unittest.main()
