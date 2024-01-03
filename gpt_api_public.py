import json
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
import mysql.connector
from mysql.connector import Error
import sys
import logging
import os

client_ld = boto3.client('lambda')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # TODO implement
    '''
    event = {
        'title':title,
        'date':date,
        'imageURL':imageURL,
        'article':article
        'source':source_url
    }
    '''
    print("Starting OpenAI...")
    client = OpenAI(
        api_key=get_secret(),
        )
    print("Retrieved key!")
    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a cybersecurity journalist."},
        {"role": "user", "content": "Paraphrase this article title: " + event['title']}
    ]
    )
    title = response.choices[0].message.content
    
    response2 = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a cybersecurity journalist."},
        {"role": "user", "content": "Summarize this article: " + event['article']}
    ]
    )
    article = response2.choices[0].message.content
    
    
    output = {
        'title':title,
        'date':event['date'],
        'imageURL':event['imageURL'],
        'article':article,
        'source':event['source']
        }
    
    print("Uploading to RDS")
    res = invokeUploadRDS(output)
    
    return res


def invokeUploadRDS(input):
    response = client_ld.invoke(
    FunctionName = 'arn:aws:lambda:us-east-1:689050894738:function:blog_gpt_api',
    InvocationType = 'RequestResponse',
    Payload = json.dumps(input)
    )
    return response
    #print(json.load(response['Payload']))


def get_secret():

    secret_name = "openai_api_key"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    print("Getting secret")

    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    print("loaded secretsmanager")
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    print("Got key")
    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    key = json.loads(secret)
    return key['openai_gpt_api_key']
    
    
