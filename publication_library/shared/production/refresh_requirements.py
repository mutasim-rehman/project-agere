"""Read-only venue refresh: flag changed/inaccessible pages; never rewrite a paper."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,urllib.request,hashlib,json,datetime
L=Path(__file__).resolve().parents[2]
def check(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=25) as response:
            data=response.read()
            return dict(url=url,http_status=response.status,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='FETCHED; HUMAN-COMPARISON-REQUIRED')
    except Exception as exc:
        return dict(url=url,status='INACCESSIBLE; NEEDS-GUIDELINE-REFRESH',error=str(exc))
def main():
    p=argparse.ArgumentParser();p.add_argument('--include-blocked',action='store_true');args=p.parse_args()
    manifest=json.loads((L/'venue_manifest.json').read_text())
    urls=sorted({url for row in manifest for url in row.get('official_sources',[]) if url.startswith('https://')})
    # Do not automatically retry known blocked binary downloads or authentication routes.
    urls=[u for u in urls if args.include_blocked or not any(s in u for s in ['scimagojr.com','authorkit27','/wp-content/uploads/','/login','peerj.com'])]
    previous_path=L/'requirements_refresh.json';previous={}
    if previous_path.exists():previous={x['url']:x for x in json.loads(previous_path.read_text()).get('pages',[])}
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,urls))
    for row in rows:
        old=previous.get(row['url'])
        row['changed_since_previous_fetch']=None if not old or not row.get('sha256') else row['sha256']!=old.get('sha256')
    result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),note='HTTP availability/hash comparison cannot verify policy meaning. Navigation changes can alter hashes. No manuscript was modified.',pages=rows)
    previous_path.write_text(json.dumps(result,indent=2));print(previous_path)
if __name__=='__main__':main()
