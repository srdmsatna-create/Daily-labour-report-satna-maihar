import unittest
from unittest.mock import patch
import update_emb_pending as m

class ZeroAttendanceTests(unittest.TestCase):
 def test_headers_and_column_numbers(self):
  for header in ('Muster Roll No.', 'e-Muster Roll Number', 'MR No.', 'E-MR No.', 'Muster Roll No.\n'):
   source=f'<table><tr><th>Sl.</th><th>Work</th><th>{header}</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>1</td><td>Road</td><td>12345</td></tr></table>'
   self.assertEqual(m.zero_mrs(m.rows(source),1),{'12345'})
 def test_mismatch_is_not_published(self):
  with self.assertRaisesRegex(ValueError,'expected=2; observed=\\[1\\]'):
   m.zero_mrs(m.rows('<tr><th>Sl.</th><th>MR No.</th></tr><tr><td>1</td><td>123</td></tr>'),2)
 def test_unknown_header_is_rejected(self):
  with self.assertRaises(ValueError):m.zero_mrs(m.rows('<tr><th>Sl.</th><th>Other No.</th></tr><tr><td>1</td><td>123</td></tr>'),1)

 def test_refreshes_summary_before_retry(self):
  parent='<tr><td>1</td><td>AHIRGAON</td><td>0</td><td>0</td><td>0</td><td><a href="/detail">1</a></td><td>0</td><td>0</td><td>0</td><td>0</td></tr>'
  root=object()
  bad=m.rows('<tr><th>Sl.</th><th>MR No.</th></tr>')
  good=m.rows('<tr><th>Sl.</th><th>MR No.</th></tr><tr><td>1</td><td>123</td></tr>')
  calls=[]
  def get(url):
   calls.append(url)
   if url==m.R42_URL:return root,'https://example.test/root'
   if url=='https://example.test/parent':return m.rows(parent),'https://example.test/parent'
   return (bad if calls.count(url)==1 else good),url
  with patch.object(m,'get',side_effect=get),patch.object(m,'block_links',return_value={'AMARPATAN':'https://example.test/parent'}),patch.object(m.time,'sleep'):
   result,_=m.load_zero_attendance()
  self.assertEqual(result,{('AMARPATAN','AHIRGAON','123')})
  self.assertEqual(calls.count('https://example.test/parent'),2)

if __name__=='__main__':unittest.main()
