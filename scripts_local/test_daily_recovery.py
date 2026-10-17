import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts_local'/f'{name}.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class RecoveryTests(unittest.TestCase):
 def test_successful_groups_are_never_refetched(self):
  runner=load('run_daily_unified');calls=[]
  def refresh(group,*args,**kwargs):
   calls.append(group)
   return {'success':group=='ok' or calls.count(group)==2}
  feeds=SimpleNamespace(GROUPS=[('ok',[],[]),('network',[],[])],refresh_group=refresh)
  states=runner.refresh_reports(feeds,ROOT,sleep=lambda _:None)
  self.assertEqual(calls,['ok','network','network'])
  self.assertEqual(states['ok']['attempts'],1);self.assertTrue(states['network']['success'])
 def test_persistent_failure_stops_after_three_attempts(self):
  runner=load('run_daily_unified');calls=[]
  def refresh(*args,**kwargs):calls.append(1);return {'success':False}
  states=runner.refresh_reports(SimpleNamespace(GROUPS=[('bad',[],[])],refresh_group=refresh),ROOT,sleep=lambda _:None)
  self.assertEqual(len(calls),3);self.assertFalse(states['bad']['success'])
 def test_child_error_is_stored_and_group_output_restored(self):
  feeds=load('update_all_tabs')
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'report.js').write_text('verified')
   (root/'fail.py').write_text("from pathlib import Path\nPath('report.js').write_text('partial')\nprint('Connection reset 10054')\nraise SystemExit(1)\n")
   state=feeds.refresh_group('broken',[['fail.py']],['report.js'],root=root)
   self.assertFalse(state['success']);self.assertIn('Connection reset 10054',state['errorTail'])
   self.assertEqual((root/'report.js').read_text(),'verified')
 def test_child_timeout_is_bounded(self):
  feeds=load('update_all_tabs')
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'slow.py').write_text('import time\ntime.sleep(10)')
   import subprocess
   with self.assertRaises(subprocess.TimeoutExpired):feeds.run_logged(['slow.py'],root,'slow',0.1)

class BrowserRetryTests(unittest.IsolatedAsyncioTestCase):
 async def test_only_failed_page_is_retried(self):
  m=load('emb_browser_reader');reader=m.BrowserReader.__new__(m.BrowserReader)
  reader.slots=asyncio.Semaphore(5);reader.read_once=AsyncMock(side_effect=[RuntimeError('reset'),('complete','url')])
  with patch.object(m.asyncio,'sleep',new_callable=AsyncMock):
   self.assertEqual(await reader.read('https://vbgramgrep.dord.gov.in/report'),('complete','url'))
  self.assertEqual(reader.read_once.await_count,2)
 async def test_permanent_refusal_is_not_retried(self):
  m=load('emb_browser_reader');reader=m.BrowserReader.__new__(m.BrowserReader)
  reader.slots=asyncio.Semaphore(5);reader.read_once=AsyncMock(side_effect=ValueError('HTTP 403'))
  with self.assertRaises(ValueError):await reader.read('https://vbgramgrep.dord.gov.in/report')
  self.assertEqual(reader.read_once.await_count,1)

if __name__=='__main__':unittest.main()
