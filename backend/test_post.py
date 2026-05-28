import json
import urllib.request

payload = {"name": "Test User", "email": "test5@example.com", "password": "secret123"}
req = urllib.request.Request('http://127.0.0.1:8000/api/auth/register', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    res = urllib.request.urlopen(req)
    print(res.status)
    print(res.read().decode())
except Exception as e:
    import traceback
    traceback.print_exc()
    if hasattr(e, 'read'):
        try:
            print(e.read().decode())
        except Exception:
            pass
