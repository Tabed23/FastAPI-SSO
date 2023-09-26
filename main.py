import json
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import requests
from starlette.config import Config
from schema.schema import Role, User
from utils.validate import retrieve_token, validate_remotely


config = Config('.env')

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

okta_url = config('OKTA_ISSUER')
api_token = '00ufe3Yd42h_W1tG42vuvKoTHK6z7U9YQPqX8kf9zq'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'SSWS {api_token}'
}

# Open, Hello World route
@app.get('/')
def read_root():
    return {'Hello': 'World'}


# Get auth token
@app.post('/token')
def login(request: Request): 
     token = retrieve_token(
        request.headers['Authorization'],
        config('OKTA_ISSUER'),
        'items'
    )
     return token




def validate(token: str = Depends(oauth2_scheme)):
    res = validate_remotely(
        token,
        config('OKTA_ISSUER'),
        config('OKTA_CLIENT_ID'),
        config('OKTA_CLIENT_SECRET')
    )

    if res:
        return True
    else:
        raise HTTPException(status_code=400)
    
# Protected, get items route
@app.get('/user', response_model=User)
def read_items(valid: bool = Depends(validate)):
    user_data = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Depp',
        'role': Role.admin,  
        'password': 'hashed_password',  
        'email': 'test@example.com',
    }

    user = User(**user_data)

    return user



@app.post('/user', response_model=dict)
def create_user(user: User, valid: bool = Depends(validate)):

    saved_user_data = {
    'profile': {
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'login': user.email
    },
    'credentials': {
        'password': {
            'value': user.password
        }
    }
}
    
    url = f'{okta_url}/api/v1/users'

    response = requests.post(url, headers=headers, data=json.dumps(saved_user_data))
    if response.status_code == 200:
        new_user = json.loads(response.text)
        print(f"User {new_user['profile']['login']} created in Okta")
    else:
        error_data = response.json()
        print(f"Failed to create user in Okta. Error: {error_data['errorSummary']}")
        return error_data

    return saved_user_data
