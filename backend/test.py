from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
res = client.post('/api/auth/login', json={'username':'test_user', 'password':'123'})
token = res.json()['data']['access_token']
print('ACCOUNTS:', client.get('/api/accounts', headers={'Authorization': 'Bearer '+token}).text)
print('SUMMARY:', client.get('/api/accounts/summary', headers={'Authorization': 'Bearer '+token}).text)
