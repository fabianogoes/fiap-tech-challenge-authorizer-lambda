import jwt
import os
from dotenv import load_dotenv
from jwt.exceptions import ExpiredSignatureError

load_dotenv()
SECRET = os.getenv("SECRET")
VERSION = "2024.8.26.1"
EFFECT_ALLOW = "Allow"
EFFECT_DENY = "Deny"

def lambda_handler(event, context):
    print("*********** the event is: *************")
    print(VERSION)
    print(event)

    token = extractToken(event)
    if token is None:
        return generateResponse(user, EFFECT_DENY, event["methodArn"])
    
    user = None
    if is_valid(token):
        try:
            print(f"SECRET={SECRET}")
            token_decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            print(token_decoded)
            
            user = token_decoded["user"]
            email = token_decoded["email"]
            cpf = token_decoded["sub"]
            principalId = cpf
            print(f"cpf={cpf}, user={user}, email={email}")

            return generateResponse(user, EFFECT_ALLOW, event["methodArn"])
        except ExpiredSignatureError:
            print(f"Expired Token={token}")
            return generateResponse(user, EFFECT_DENY, event["methodArn"])
        except Exception as error:
            print(f"Validation token={token} error = {error}")
            return generateResponse(user, EFFECT_DENY, event["methodArn"])
    else:
        return generateResponse(user, EFFECT_DENY, event["methodArn"])
           
    
def extractToken(event):
    token = None
    if "authorizationToken" in event:
        token = event["authorizationToken"]
    elif "authorizationtoken" in event:
        token = event["authorizationtoken"]
    elif "headers" in event:
        headers = event["headers"]
        print(headers)
        if "authorizationToken" in headers:
            token = headers["authorizationToken"]
        elif "authorizationtoken" in headers:
            token = headers["authorizationtoken"]
        else:
            print("token not found in headers")
    else:
        print("token not found")
    
    print(f"token={token}")    
    return token

def generateResponse(user, effect, methodArn):
    first = methodArn.split(":")
    second = first[5].split("/")
    print(f"first={first}")
    print(f"second={second}")
    # first=['arn', 'aws', 'execute-api', 'us-east-1', '758397526889', '4m5ipmqfdg/default/GET/env']
    # second=['arn:aws:execute-api:us-east-1:758397526889:4m5ipmqfdg', 'default', 'GET', 'env']
    region = first[3]
    accountId = first[4]
    apiId = second[0]
    apiStage = second[1]
    resource = f"arn:aws:execute-api:{region}:{accountId}:{apiId}/{apiStage}/*/*"
    print(f"resource={resource}")    
    
    response = { 
        "principalId": user, 
        "policyDocument": { 
            "Version": "2012-10-17", 
            "Statement": [
                {
                    "Action": "execute-api:Invoke", 
                    "Effect": effect,
                    "Resource": [resource]
                }
            ] 
        }
    }
    print(f"response={response}")
    
    return response


def generateAllow(principalId, resource):
    return generatePolicy(principalId, 'Allow', resource)


def generateDeny(principalId, resource):
    return generatePolicy(principalId, 'Deny', resource)


def is_valid(token):
    try:
        jwt.get_unverified_header(token)
        return True
    except ExpiredSignatureError as error:
        print(f"Invalid Token={token} error={error}")
        return False
    except Exception as error:
        print(f"Invalid Token={token} error={error}")
        return False
