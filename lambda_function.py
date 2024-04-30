import jwt
import os
from dotenv import load_dotenv
from jwt.exceptions import ExpiredSignatureError

load_dotenv()
SECRET = os.getenv("SECRET")
VERSION = "2024-04-29-1"

def lambda_handler(event, context):
    print("*********** the event is: *************")
    print(VERSION)
    print(event)

    headers = event["headers"]
    print(headers)

    token =headers["authorizationtoken"]
    print(f"authorizationtoken={token}")
            
    auth = False
    if is_valid(token):
        try:
            print(f"SECRET={SECRET}")
            token_decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            print(token_decoded)
            
            user = token_decoded["user"]
            email = token_decoded["email"]
            cpf = token_decoded["sub"]
            auth = True
            
            print(f"cpf={cpf}, user={user}, email={email}")
        except ExpiredSignatureError:
            print("Expired Token")
        except:
            print("Validation token error")
    else:
        auth = 'false'
        
    # authResponse = { "principalId": user, "policyDocument": { "Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Resource": ["arn:aws:execute-api:us-east-1:758397526889:0no1axjaq1/*/*/*"], "Effect": auth}] }}
    authResponse = {"isAuthorized": auth}
    return authResponse


def is_valid(token):
    try:
        jwt.get_unverified_header(token)
        return True
    except ExpiredSignatureError as error:
        return False
