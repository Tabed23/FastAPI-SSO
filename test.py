#Create user


import asyncio
from okta.client import Client as OktaClient
from okta import models



okta_url = 'https://dev-37647126.okta.com'
api_token = 'a00ufe3Yd42h_W1tG42vuvKoTHK6z7U9YQPqX8kf9zq'
config = {
    'orgUrl': okta_url,
    'token': api_token
}

# Create Password
password = models.PasswordCredential({
    'value': 'Password!123'
})

# Create User Credentials
user_creds = models.UserCredentials({
    'password': password
})

# Create User Profile and CreateUser Request
user_profile = models.UserProfile()
user_profile.first_name = 'Omid'
user_profile.last_name = 'Raha'
user_profile.email = 'omid@example.com'
user_profile.login = 'omid@example.com'

create_user_request = models.CreateUserRequest({
    'credentials': user_creds,
    'profile': user_profile
})


async def main():
    async with OktaClient(config) as client:
        res = await client.create_user(create_user_request, {'activate': True, })
        print('User created, info: {}'.format(res))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
