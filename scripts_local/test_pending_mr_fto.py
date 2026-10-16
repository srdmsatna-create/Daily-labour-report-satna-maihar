import unittest
from update_pending_mr_fto import summarize,rows,build,BLOCKS
HEAD=['SNo.','Panchayat Name','Muster roll number','Technical Staff','Record No.','Work Code','date of Closure of Muster Roll','Muster Roll Filling Status','Wage date','Wagelist No.','FTO No.','FTO date','Date of 1st sign','Date of 2nd sign']
def fixture(items):
 def tr(v):return '<tr>'+''.join('<td>'+str(x)+'</td>' for x in v)+'</tr>'
 return rows(tr(HEAD)+''.join(tr([i+1,'GP','123','Staff',1,'1712001001/WC/123','01-10-2026','Filled','02-10-2026','WL1']+v) for i,v in enumerate(items)))
class TrackingTests(unittest.TestCase):
 def test_duplicate_mr_is_not_double_counted(self):
  d=summarize(fixture([['','','Pending for signature of 1st Signatory','']]*2))['groups']['GP']
  self.assertEqual((d['mr'],d['first'],d['missingFtoFirst']),(1,1,1))
 def test_multiple_ftos_keep_unique_mr_and_unique_orders(self):
  d=summarize(fixture([['FTO1','03-10-2026','03-10-2026','Pending for signature of 2nd Signatory'],['FTO2','03-10-2026','03-10-2026','Pending for signature of 2nd Signatory']]))['groups']['GP']
  self.assertEqual((d['second'],d['knownSecond']),(1,2))
 def test_signed_rows_are_not_signature_pending(self):
  d=summarize(fixture([['FTO1','03-10-2026','03-10-2026','04-10-2026']]))['groups']['GP']
  self.assertEqual((d['mr'],d['first'],d['second']),(1,0,0))
 def test_dates_and_pending_text_are_preserved(self):
  result=summarize(fixture([['FTO1','03-10-2026','04-10-2026','Pending for signature of 2nd Signatory since 5 days']]))
  row=result['details'][0]
  self.assertEqual([row[k] for k in ('closureDate','wageListDate','ftoDate','firstSignDate','secondSignDate')],['01-10-2026','02-10-2026','03-10-2026','04-10-2026','Pending for signature of 2nd Signatory since 5 days'])
  self.assertTrue(row['secondPending'])
 def test_missing_table_and_incomplete_coverage_fail(self):
  with self.assertRaises(ValueError):summarize(rows('<p>No report</p>'))
  with self.assertRaises(ValueError):build({'AMARPATAN':{'groups':{}}})
if __name__=='__main__':unittest.main()
