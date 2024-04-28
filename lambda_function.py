import jwt
import os
from dotenv import load_dotenv
from jwt.exceptions import ExpiredSignatureError

load_dotenv()
SECRET = os.getenv("SECRET")
VERSION = "2024-04-28-2"

def lambda_handler(event, context):
    print("*********** the event is: *************")
    print(VERSION)
    print(event)

    token = event['authorizationToken']    
    auth = 'Deny'
    if is_valid(token):
        auth = 'Allow'

        token_decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = token_decoded["user"]
        email = token_decoded["email"]
        print(f"user={user}, email={email}")
    else:
        auth = 'Deny'
        
    authResponse = { "principalId": user, "policyDocument": { "Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Resource": ["arn:aws:execute-api:us-east-1:758397526889:0no1axjaq1/*/*/*"], "Effect": auth}] }}
    return authResponse


def is_valid(token):
    try:
        jwt.get_unverified_header(token)
        return True
    except ExpiredSignatureError as error:
        return False
