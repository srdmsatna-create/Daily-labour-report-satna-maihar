import unittest
import tempfile,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import update_emb_pending as emb
import update_all_tabs as feeds
from unittest.mock import patch

class CoverageRecoveryTests(unittest.TestCase):
 def test_retries_only_unread_gps_and_restarts_session(self):
  calls=[];restarts=[]
  def one(t):
   calls.append(t)
   if t=='bad' and calls.count(t)==1:raise RuntimeError('Target crashed')
   return t
  result,fail=emb.read_gp_jobs(['ok','bad'],one,restart=lambda:restarts.append(True))
  self.assertEqual(sorted(result),['bad','ok']);self.assertEqual(fail,[])
  self.assertEqual(calls.count('ok'),1);self.assertEqual(calls.count('bad'),2)
  self.assertEqual(len(restarts),1)
 def test_persistent_unread_gp_is_not_silently_zero(self):
  def one(t):raise TimeoutError('source unavailable')
  result,fail=emb.read_gp_jobs(['GP'],one)
  self.assertEqual(result,[]);self.assertEqual(len(fail),1)
 def test_partial_snapshot_cannot_be_marked_verified(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'data').mkdir();(root/'scripts_local').mkdir()
   (root/'data/emb-pending-latest.json').write_text(json.dumps({'failedGP':5}))
   with patch.object(feeds.runpy,'run_path',return_value={'validate':lambda d:None}):
    with self.assertRaisesRegex(ValueError,'5 unread GPs'):feeds.validate('emb_pending',root)

if __name__=='__main__':unittest.main()
