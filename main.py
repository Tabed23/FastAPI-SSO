import json
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
import requests
from starlette.config import Config
from schema.schema import User
from utils.validate import retrieve_token, validate_remotely
from okta.client import Client as OktaClient
from fastapi import Path


config = Config(".env")

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

okta_url = config("OKTA_DOMAIN")
api_token = "00ufe3Yd42h_W1tG42vuvKoTHK6z7U9YQPqX8kf9zq"
client_id = config("OKTA_CLIENT_ID")
client_screat = config("OKTA_CLIENT_SECRET")

okta_client_config = {"orgUrl": okta_url, "token": api_token}
okta_client = OktaClient(okta_client_config)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"SSWS {api_token}",
}


# Get auth token
@app.post("/token")
def login(request: Request):
    token = retrieve_token(
        request.headers["authorization"], config("OKTA_ISSUER"), "items"
    )
    return token


# Validate
def validate(token: str = Depends(oauth2_scheme)):
    res = validate_remotely(
        token,
        config("OKTA_ISSUER"),
        config("OKTA_CLIENT_ID"),
        config("OKTA_CLIENT_SECRET"),
    )

    if res:
        return True
    else:
        raise HTTPException(status_code=400)


# User login endpoint
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_auth_data = {
        "username": form_data.username,
        "password": form_data.password,
    }
    auth_response = requests.post(
        f"{okta_url}/api/v1/authn", headers=headers, data=json.dumps(user_auth_data)
    )

    if auth_response.status_code == 200:
        auth_result = json.loads(auth_response.text)
        if auth_result["status"] == "SUCCESS":
            session_token = auth_result[
                "sessionToken"
            ]
            return {"message": "User Authenticated", "session_token": session_token}
        else:
            raise HTTPException(status_code=401, detail="Authentication failed")
    else:
        raise HTTPException(status_code=400, detail="Failed to authenticate user")


# User signup endpoint
@app.post("/signup")
def signup(user: User, valid: bool = Depends(validate)):
    # Create a new user in Okta
    saved_user_data = {
        "profile": {
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "login": user.email,
        },
        "credentials": {"password": {"value": user.password}},
    }

    url = f"{okta_url}/api/v1/users"
    response = requests.post(url, headers=headers, data=json.dumps(saved_user_data))
    if response.status_code == 200:
        new_user = json.loads(response.text)
        print(f"User {new_user['profile']['login']} created in Okta")
        return {"message": "User registered successfully", "new_user": new_user}
    else:
        error_data = response.json()
        print(f"Failed to create user in Okta. Error: {error_data['errorSummary']}")
        raise HTTPException(status_code=400, detail="Failed to register user")


@app.get("/current/user/signup")
def me(valid: bool = Depends(validate)):

    url = f"{okta_url}/api/v1/users/me"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cur_user = json.loads(response.text)
        return {"user": cur_user}
    else:
        error_data = response.json()
        print(
            f"Failed to get current user in Okta. Error: {error_data['errorSummary']}"
        )
        raise HTTPException(status_code=400, detail="Failed to get current user")


@app.delete("/user/{user_id}/sessions")
def delete_user_session(
    user_id: str = Path(..., title="User ID"), valid: bool = Depends(validate)
):
    session_delete_url = f"{okta_url}/api/v1/users/{user_id}/sessions"

    response = requests.delete(session_delete_url, headers=headers)

    if response.status_code == 204:
        return {"message": f"Session for user {user_id} deleted successfully."}
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to delete user session."
        )


@app.delete("/user/{user_id}")
def delete_user(user_id: str = Path(..., title="User ID"), valid: bool = Depends(validate)):
    delete_url = f"{okta_url}/api/v1/users/{user_id}"
    response = requests.delete(delete_url, headers=headers)

    if response.status_code == 204:
        return {"message": f"u  ser {user_id} deleted successfully."}
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to delete user."
        )
      


@app.get('/list_users')
def list_users(valid: bool = Depends(validate)):
    get_list =  f"{okta_url}//api/v1/users?limit=25"
    response = requests.get(get_list, headers=headers)

    if response.status_code == 200:
        users = response.json()  # Parse JSON response
        return {"users": users}
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to get user"
        )
      

@app.get("/user/{user_id}")
def get_user(user_id: str = Path(..., title="User ID"), valid: bool = Depends(validate)):
    get_url = f"{okta_url}/api/v1/users/{user_id}"
    response = requests.get(get_url, headers=headers)

    if response.status_code == 200:
        user = response.json()  # Parse JSON response
        return {"user": user}
    else:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to delete user."
        )


@app.get('/user-info')
def get_user_info(valid: bool = Depends(validate)):
    response = requests.get(okta_url, headers=headers)
    if response.status_code == 200:
            user_info = response.text
            return {"user_info": user_info}
    else:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to get user info"
            )