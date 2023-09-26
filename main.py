import json
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
from starlette.config import Config
from schema.schema import Role, User
from utils.validate import retrieve_token, validate_remotely
from okta.client import Client as OktaClient


config = Config('.env')

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

okta_url = config('OKTA_DOMAIN')
api_token = '00ufe3Yd42h_W1tG42vuvKoTHK6z7U9YQPqX8kf9zq'


okta_client_config = {
    'orgUrl': okta_url,
    'token': api_token
}
okta_client = OktaClient(okta_client_config)

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'SSWS {api_token}'
}


# Get auth token
@app.post('/token')
def login(request: Request): 
     token = retrieve_token(
        request.headers['authorization'],
        config('OKTA_ISSUER'),
        'items'
    )
     return token



# Validate
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
    


# TODO: Implement it properly
# User login endpoint
@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user with Okta
    user_auth_data = {
        'username': form_data.username,
        'password': form_data.password,
    }
    auth_response = requests.post(f'{okta_url}/api/v1/authn', headers=headers, data=json.dumps(user_auth_data))

    if auth_response.status_code == 200:
        auth_result = json.loads(auth_response.text)
        if auth_result['status'] == 'SUCCESS':
            # User authentication successful, return an access token
            access_token_data = {
                'grant_type': 'password',
                'username': form_data.username,
                'password': form_data.password,
                'scope': 'openid profile email',  # Define the desired scopes here
            }
            token_response = requests.post(f'{okta_url}/v1/token', headers=headers, data=access_token_data)

            if token_response.status_code == 200:
                token_data = json.loads(token_response.text)
                return {'access_token': token_data['access_token'], 'token_type': 'bearer'}
            else:
                raise HTTPException(status_code=400, detail='Failed to obtain access token')
        else:
            raise HTTPException(status_code=401, detail='Authentication failed')
    else:
        raise HTTPException(status_code=400, detail='Failed to authenticate user')





# User signup endpoint
@app.post('/signup')
def signup(user: User, valid: bool = Depends(validate)):
    # Create a new user in Okta
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
        return {'message': 'User registered successfully'}
    else:
        error_data = response.json()
        print(f"Failed to create user in Okta. Error: {error_data['errorSummary']}")
        raise HTTPException(status_code=400, detail='Failed to register user')