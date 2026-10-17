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

from unittest.mock import AsyncMock, MagicMock, patch
import update_pending_mr_fto as tracking
class PostbackTests(unittest.IsolatedAsyncioTestCase):
 async def test_already_selected_option_does_not_wait_for_nonexistent_request(self):
  page=MagicMock();control=page.locator.return_value
  control.locator.return_value.all_text_contents=AsyncMock(return_value=[' MADHYA PRADESH '])
  with patch.object(tracking,'postback',new_callable=AsyncMock) as wait:
   await tracking.select_report_option(page,'#state','MADHYA PRADESH')
   wait.assert_not_awaited()
  control.select_option.assert_not_called()
 async def test_updatepanel_response_does_not_require_navigation(self):
  page=MagicMock();page.url='https://example.test/report.aspx?x=1'
  response=MagicMock();response.status=200;response.finished=AsyncMock()
  future=__import__('asyncio').get_running_loop().create_future();future.set_result(response)
  manager=MagicMock();manager.__aenter__=AsyncMock(return_value=type('Pending',(),{'value':future})());manager.__aexit__=AsyncMock(return_value=False)
  page.expect_response.return_value=manager
  page.wait_for_load_state=AsyncMock();page.wait_for_function=AsyncMock();action=AsyncMock()
  await tracking.postback(page,action,'select state')
  action.assert_awaited_once();response.finished.assert_awaited_once()
  page.expect_navigation.assert_not_called()
 async def test_transient_failure_retries_only_failed_block(self):
  async def block(context,b,n):
   calls.append(b)
   if b=='MAIHAR' and calls.count(b)==1:raise TimeoutError('temporary')
   return b
  calls=[]
  with patch.object(tracking,'BLOCKS',{'SATNA':93,'MAIHAR':115}),patch.object(tracking,'fetch_block',side_effect=block),patch.object(tracking.asyncio,'sleep',new_callable=AsyncMock),patch.object(tracking,'build',side_effect=lambda x:x):
   result=await tracking.fetch(object())
  self.assertEqual(calls,['SATNA','MAIHAR','MAIHAR']);self.assertEqual(set(result),{'SATNA','MAIHAR'})

if __name__=='__main__':unittest.main()
