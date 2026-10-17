"""One entry point: isolated refresh, validation, then one publication."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def run(args, root=ROOT):
    subprocess.run(args, cwd=root, check=True)

def publish(stage):
    # A refresh can take hours; main may advance while sources are fetched.
    for attempt in range(3):
        run(['git', 'fetch', 'origin', '+refs/heads/main:refs/remotes/origin/main'], stage)
        result = subprocess.run(['git', 'rebase', 'origin/main'], cwd=stage)
        if result.returncode:
            subprocess.run(['git', 'rebase', '--abort'], cwd=stage)
            raise RuntimeError('Remote report conflict. Validated commit retained at ' + str(stage) + '; no reports overwritten.')
        result = subprocess.run(['git', 'push', 'origin', 'HEAD:main'], cwd=stage)
        if result.returncode == 0:
            return
        print('Publication failed; fetching latest main before retry ' + str(attempt + 1), flush=True)
    raise RuntimeError('Publication failed after 3 attempts. Validated commit retained at ' + str(stage))

def prevent_console_pause():
    # Quick Edit selection pauses a Windows console process until Esc.
    if os.name != 'nt':return
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        mode = ctypes.c_uint()
        handle = kernel.GetStdHandle(-10)
        if kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel.SetConsoleMode(handle, (mode.value | 0x0080) & ~0x0040)
    except (AttributeError, OSError):pass

def refresh_reports(feeds, stage, sleep=time.sleep):
    states = {}
    for attempt in range(1, 4):
        pending = [(g,c,f) for g,c,f in feeds.GROUPS if not states.get(g,{}).get('success')]
        if not pending:break
        if attempt > 1:
            print('Automatic recovery: retrying only failed reports: ' + ', '.join(g for g,_,_ in pending), flush=True)
            sleep(5 * (attempt - 1))
        for group, commands, files in pending:
            print(f'[{group}] attempt {attempt}/3', flush=True)
            state = feeds.refresh_group(group, commands, files, root=stage)
            state['attempts'] = attempt
            states[group] = state
            print(group + ': ' + ('VERIFIED' if state['success'] else 'FAILED; previous verified group retained'), flush=True)
    return states

def main():
    prevent_console_pause()
    os.environ.setdefault('PMAY_FETCH_CACHE_DIR', str(ROOT / 'data' / 'pmayg-fetch-cache'))
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--publish-verified', action='store_true', help='Publish only fully validated independent groups even when another group fails')
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
        run(['git', 'fetch', 'origin', '+refs/heads/main:refs/remotes/origin/main'])
        stage = Path(tempfile.mkdtemp(prefix='SRDM_DAILY_')) / 'report'
        run(['git', 'worktree', 'add', '--detach', str(stage), 'origin/main'])
        spec = importlib.util.spec_from_file_location('daily_feeds', stage / 'scripts_local/update_all_tabs.py')
        feeds = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(feeds)
        states = refresh_reports(feeds, stage)
        status = {'checkedAt':datetime.now(timezone.utc).isoformat(), 'schedule':'08:00 Asia/Kolkata',
                  'reports':states, 'success':all(x['success'] for x in states.values())}
        (stage / 'all-tabs-auto-status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        # Failed groups remain atomic; optional publication includes successful groups only.
        if not status['success']:
            failure_root = Path(os.environ.get('SRDM_DAILY_REPO') or ROOT)
            failure = failure_root / 'daily-update-last-failure.json'
            failure.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
            bundle = failure_root / 'daily-update-diagnostics.zip'
            with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.write(failure, failure.name)
                log = failure_root / 'daily-all-reports.log'
                if log.is_file():archive.write(log, log.name)
                for folder in ('gp-emuster-debug','yuktdhara-received-debug','daily-run-logs'):
                    debug = stage / 'data' / folder
                    if debug.exists():
                        for item in sorted(debug.glob('*')):
                            if item.is_file():
                                archive.write(item, folder + '/' + item.name)
            print('Current-run diagnostics saved: ' + str(bundle), flush=True)
            if not args.publish_verified or not any(x['success'] for x in states.values()):
                raise RuntimeError('Full daily refresh incomplete. Live reports unchanged; diagnostics: ' + str(failure))
        eligible = list(dict.fromkeys(f for group, _, outputs in feeds.GROUPS if states[group]['success'] for f in outputs))
        files = [f for f in eligible + ['all-tabs-auto-status.json'] if (stage / f).exists()]
        if not args.publish:
            print('VERIFIED: publication disabled. Prepared files: ' + str(stage), flush=True)
            return 0
        run(['git', 'config', 'user.name', 'SRDM Daily Updater'], stage)
        run(['git', 'config', 'user.email', 'srdm-updater@users.noreply.github.com'], stage)
        run(['git', 'add', '--'] + files, stage)
        changed = subprocess.run(['git','diff','--cached','--quiet'], cwd=stage).returncode
        if changed == 1:
            run(['git','commit','-m','Verified daily report groups ' + status['checkedAt']], stage)
            publish(stage)
        elif changed != 0:
            raise RuntimeError('Cannot check prepared report changes')
        cleanup = True
        if not status['success']:
            failed = ', '.join(name for name, state in states.items() if not state['success'])
            print('PARTIAL: validated reports published. Pending reports: ' + failed + '; previous verified data retained.', flush=True)
            return 1
        print('SUCCESS: every report validated; one complete publication.', flush=True)
        return 0
    finally:
        lock.unlink(missing_ok=True)
        if stage is not None and cleanup:
            # Only this run's disposable worktree: fetchers leave debug files
            # outside the committed output list. Cleanup cannot undo a push.
            try:
                run(['git','worktree','remove','--force',str(stage)])
                stage.parent.rmdir()
            except (OSError, subprocess.CalledProcessError) as exc:
                print('WARNING: Reports published successfully; temporary cleanup incomplete: ' + str(exc), flush=True)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
