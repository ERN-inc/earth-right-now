"""Discover ERN's current YouTube live video without a paid API key."""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CHANNEL_LIVE = 'https://www.youtube.com/@earth_right_now/live'
OUTPUT = Path(__file__).resolve().parents[1] / 'live.json'


def main():
    command = [sys.executable, '-m', 'yt_dlp', '--dump-single-json', '--no-playlist',
               '--skip-download', '--no-warnings', '--socket-timeout', '20', CHANNEL_LIVE]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=100)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f'Lookup failed; retaining previous status: {exc}', file=sys.stderr)
        return 1
    if result.returncode != 0:
        error = result.stderr.lower()
        if 'the channel is not currently live' in error:
            info = {'live_status': 'not_live'}
            print('Channel is offline; recording offline status')
        else:
            print('Lookup failed; retaining previous status: ' + result.stderr[-1200:], file=sys.stderr)
            return 1
    else:
        try:
            info = json.loads(result.stdout)
        except json.JSONDecodeError:
            print('Invalid extractor output; retaining previous status', file=sys.stderr)
            return 1
    status = info.get('live_status')
    video_id = info.get('id')
    if status == 'is_live' and re.fullmatch(r'[A-Za-z0-9_-]{11}', str(video_id)):
        payload = {'status': 'live', 'videoId': video_id}
    elif status in ('not_live', 'was_live', 'post_live', 'is_upcoming'):
        payload = {'status': 'offline', 'videoId': None}
    else:
        print(f'Uncertain status {status!r}; retaining previous status', file=sys.stderr)
        return 1
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding='utf-8'))
            if all(previous.get(key) == value for key, value in payload.items()):
                print('Status unchanged; no update required')
                return 0
        except (OSError, ValueError):
            pass
    payload['checkedAt'] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(payload)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
