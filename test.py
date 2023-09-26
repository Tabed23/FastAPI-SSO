#Create user

import requests
import json

okta_url = 'https://dev-37647126.okta.com/oauth2/default'
api_token = 'a00ufe3Yd42h_W1tG42vuvKoTHK6z7U9YQPqX8kf9zq'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'SSWS {api_token}'
}

user_data = {
    'profile': {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@email.com',
        'login': 'john@email.com'
    },
    'credentials': {
        'password': {
            'value': 'P@ssw0rd'
        }
    }
}

url = f'{okta_url}/api/v1/users'

response = requests.post(url, headers=headers, data=json.dumps(user_data))
if response.status_code == 200:
    new_user = json.loads(response.text)
    print(f"User {new_user['profile']['login']} created in Okta")
else:
    print("Failed to create user in Okta")
    
print(response.text)