import json
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
import mysql.connector
from mysql.connector import Error
import sys
import logging
import os

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_proxy_host = os.environ['RDS_PROXY_HOST']
db_name = os.environ['DB_NAME']

connection_config = {
    'host': rds_proxy_host,
    'user': user_name,
    'password': password,
    'database': db_name
}

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
    client = OpenAI(
        api_key=get_secret(),
        )
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
        
    res = uploadToRDS(output)
    
    return {
        'statusCode': res['statusCode'],
        'body': json.dumps('Uploaded to RDS!')
    }



def get_secret():

    secret_name = "openai_api_key"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    key = json.loads(secret)
    return key['openai_gpt_api_key']
    
    
def uploadToRDS(input):
    try:
        connection = mysql.connector.connect(**connection_config)
        if connection.is_connected():
            cursor = connection.cursor()
            data = [(input['date'],input['title'],input['article'],input['imageURL'],input['source'])]
            query = "INSERT INTO Articles (date_published,title, article,imageURL,source) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(query, data)
            connection.commit()
            print(cursor.rowcount, "record(s) inserted.")
    except Error as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit(1)
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded")
    return {
        'statusCode': 200,
        'body': 'Data inserted successfully'
    }