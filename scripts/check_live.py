"""Discover ERN's current YouTube live video without a paid API key."""
import json
import os
import urllib.parse
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CHANNEL_LIVE = 'https://www.youtube.com/@earth_right_now/live'
OUTPUT = Path(__file__).resolve().parents[1] / 'live.json'


def fallback_live_page():
    """Use public channel page only when it explicitly says live now."""
    req = urllib.request.Request(CHANNEL_LIVE, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read(3000000).decode('utf-8', errors='replace')
    except OSError as exc:
        print(f'Fallback unavailable: {exc}', file=sys.stderr)
        return None
    if not re.search(r'"isLiveNow"\s*:\s*true', html):
        return None
    ids = re.findall(r'"videoId"\s*:\s*"([A-Za-z0-9_-]{11})"', html)
    return {'live_status': 'is_live', 'id': ids[0]} if ids else None


def official_api_lookup():
    key = os.environ.get('YOUTUBE_API_KEY')
    channel = os.environ.get('YOUTUBE_CHANNEL_ID')
    if not key or not channel:
        print('YouTube API: credentials missing; using legacy lookup')
        return None
    if not re.fullmatch(r'UC[A-Za-z0-9_-]{22}', channel):
        print('YouTube API: invalid channel ID', file=sys.stderr)
        return None
    params = urllib.parse.urlencode({'part':'snippet','channelId':channel,'eventType':'live','type':'video','maxResults':'5','key':key})
    try:
        with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/search?' + params, timeout=20) as response:
            data = json.load(response)
    except (OSError, ValueError) as exc:
        print(f'YouTube API: request failed ({type(exc).__name__}); using legacy lookup', file=sys.stderr)
        return None
    for item in data.get('items', []):
        video_id = item.get('id', {}).get('videoId')
        if re.fullmatch(r'[A-Za-z0-9_-]{11}', str(video_id)):
            print(f'YouTube API: live detected, videoId={video_id}')
            return {'live_status':'is_live','id':video_id}
    print('YouTube API: no live video returned; reporting offline')
    return {'live_status':'not_live'}

def main():
    info = official_api_lookup()
    if info is not None:
        return write_status(info)
    return legacy_lookup()


def legacy_lookup():
    command = [sys.executable, '-m', 'yt_dlp', '--dump-single-json', '--no-playlist',
               '--skip-download', '--no-warnings', '--socket-timeout', '20', CHANNEL_LIVE]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=100)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f'Primary lookup failed: {exc}', file=sys.stderr)
        result = None
    if result is None or result.returncode != 0:
        error = result.stderr.lower() if result is not None else ''
        if 'the channel is not currently live' in error:
            info = {'live_status': 'not_live'}
            print('Channel is offline; recording offline status')
        else:
            print('Primary lookup blocked; trying public channel page', file=sys.stderr)
            info = fallback_live_page()
            if info is None:
                print('Unverified state; retaining previous status')
                return 0
    else:
        try:
            info = json.loads(result.stdout)
        except json.JSONDecodeError:
            print('Invalid extractor output; retaining previous status', file=sys.stderr)
            return 1
    return write_status(info)


def write_status(info):
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
