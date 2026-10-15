"""Upload files to Dropbox from a RunPod pod started by the runpod-ops function.

    python3 upload.py /basic1000-backup/grammar-videos file1.zip file2.zip

The pod never holds a Dropbox key: it asks runpod-ops (REPORT_URL, with its own RUN_ID and
REPORT_TOKEN) for a short-lived access token, uploads in 64 MB pieces (upload sessions), and checks
each file's size on Dropbox afterwards. Existing files of the same name are replaced.
"""
import json
import os
import sys
import urllib.request

CHUNK = 64 * 1024 * 1024


def token():
    body = json.dumps({'action': 'dropbox_token', 'run_id': os.environ['RUN_ID'], 'token': os.environ['REPORT_TOKEN']}).encode()
    req = urllib.request.Request(os.environ['REPORT_URL'], data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['access_token']


def call(tok, url, arg, data=b'', content=True):
    h = {'Authorization': 'Bearer ' + tok}
    if content:
        h['Dropbox-API-Arg'] = json.dumps(arg)
        h['Content-Type'] = 'application/octet-stream'
    else:
        h['Content-Type'] = 'application/json'
        data = json.dumps(arg).encode()
    req = urllib.request.Request(url, data=data, headers=h, method='POST')
    with urllib.request.urlopen(req, timeout=600) as r:
        txt = r.read()
        return json.loads(txt) if txt else {}


def upload(tok, path, dest):
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        first = f.read(CHUNK)
        sid = call(tok, 'https://content.dropboxapi.com/2/files/upload_session/start', {'close': False}, first)['session_id']
        off = len(first)
        while off < size:
            part = f.read(CHUNK)
            call(tok, 'https://content.dropboxapi.com/2/files/upload_session/append_v2', {'cursor': {'session_id': sid, 'offset': off}, 'close': False}, part)
            off += len(part)
            print(f'  {os.path.basename(path)}: {off * 100 // size}%', flush=True)
        meta = call(tok, 'https://content.dropboxapi.com/2/files/upload_session/finish',
                    {'cursor': {'session_id': sid, 'offset': off}, 'commit': {'path': dest, 'mode': 'overwrite', 'mute': True}})
    check = call(tok, 'https://api.dropboxapi.com/2/files/get_metadata', {'path': dest}, content=False)
    ok = check.get('size') == size
    print(f'{dest}: {size} bytes uploaded, Dropbox has {check.get("size")} -> {"OK" if ok else "MISMATCH"}', flush=True)
    return ok


def main():
    folder, files = sys.argv[1].rstrip('/'), sys.argv[2:]
    if not folder.startswith('/basic1000-backup/'):
        sys.exit('only folders inside /basic1000-backup/ may be written')
    tok = token()
    ok = all(upload(tok, p, folder + '/' + os.path.basename(p)) for p in files)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
