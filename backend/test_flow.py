import json
import urllib.request

BASE = 'http://127.0.0.1:8000'

def post(path, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        res = urllib.request.urlopen(req)
        return res.status, res.read().decode()
    except Exception as e:
        print('Error:', e)
        try:
            print(e.read().decode())
        except Exception:
            pass
        raise

# Login
email = 'test5@example.com'
password = 'secret123'
status, body = post('/api/auth/login', {'email': email, 'password': password})
print('login status', status, body)
resp = json.loads(body)
token = resp['access_token']

# Post meals
meals = [
    {'food_name':'Idli','quantity':2,'unit':'piece','calories':160,'protein':6,'carbs':30,'fats':1,'meal_type':'breakfast'},
    {'food_name':'Rice and curry','quantity':1,'unit':'plate','calories':600,'protein':10,'carbs':80,'fats':20,'meal_type':'lunch'},
    {'food_name':'Chapati','quantity':2,'unit':'piece','calories':200,'protein':6,'carbs':34,'fats':4,'meal_type':'dinner'},
]
for m in meals:
    s,b = post('/api/meals/', m, token)
    print('post meal', s, b)
