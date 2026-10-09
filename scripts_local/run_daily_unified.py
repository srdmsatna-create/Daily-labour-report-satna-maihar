"""One entry point: isolated refresh, validation, then one publication."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def run(args, root=ROOT):
    subprocess.run(args, cwd=root, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    lock = ROOT / '.unified-daily.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit('Another daily update is running; no second copy started.')
    os.close(fd)
    stage = None
    cleanup = False
    try:
        run(['git', 'fetch', 'origin', 'main'])
        stage = Path(tempfile.mkdtemp(prefix='SRDM_DAILY_')) / 'report'
        run(['git', 'worktree', 'add', '--detach', str(stage), 'origin/main'])
        spec = importlib.util.spec_from_file_location('daily_feeds', stage / 'scripts_local/update_all_tabs.py')
        feeds = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(feeds)
        states = {}
        for index, (group, commands, files) in enumerate(feeds.GROUPS, 1):
            print(f'[{index}/{len(feeds.GROUPS)}] {group}', flush=True)
            states[group] = feeds.refresh_group(group, commands, files, root=stage)
            print(group + ': ' + ('VERIFIED' if states[group]['success'] else 'FAILED; complete previous group retained'), flush=True)
        status = {'checkedAt':datetime.now(timezone.utc).isoformat(), 'schedule':'08:00 Asia/Kolkata',
                  'reports':states, 'success':all(x['success'] for x in states.values())}
        (stage / 'all-tabs-auto-status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        # A failed refresh publishes no report files or partial source status.
        if not status['success']:
            failure_root = Path(os.environ.get('SRDM_DAILY_REPO') or ROOT)
            failure = failure_root / 'daily-update-last-failure.json'
            failure.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
            raise RuntimeError('Full daily refresh incomplete. Live reports unchanged; diagnostics: ' + str(failure))
        files = [f for f in feeds.OUTPUTS if (stage / f).exists()]
        if not args.publish:
            print('VERIFIED: publication disabled. Prepared files: ' + str(stage), flush=True)
            return 0
        run(['git', 'config', 'user.name', 'SRDM Daily Updater'], stage)
        run(['git', 'config', 'user.email', 'srdm-updater@users.noreply.github.com'], stage)
        run(['git', 'add', '--'] + files, stage)
        changed = subprocess.run(['git','diff','--cached','--quiet'], cwd=stage).returncode
        if changed == 1:
            run(['git','commit','-m','Verified complete daily reports ' + status['checkedAt']], stage)
            run(['git','push','origin','HEAD:main'], stage)
        elif changed != 0:
            raise RuntimeError('Cannot check prepared report changes')
        cleanup = True
        print('SUCCESS: every report validated; one complete publication.', flush=True)
        return 0
    finally:
        lock.unlink(missing_ok=True)
        if stage is not None and cleanup:
            run(['git','worktree','remove',str(stage)])
            stage.parent.rmdir()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
