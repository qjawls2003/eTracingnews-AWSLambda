import json
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
import logging
import hashlib
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from botocore.exceptions import ClientError


client_ld = boto3.client('lambda')
client_s3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # TODO implement
    
    host = 'search-blognewsos-3b5n5ccmivrx6jqjtdcz3qe4si.us-east-1.es.amazonaws.com' 
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)
    try:
        client = OpenSearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = auth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection,
            pool_maxsize = 20
        )
    except ClientError as e:
        raise e
    
    file = getFromS3()
    entries = json.loads(file['Body'].read().decode('utf-8'))
    for data in entries:
        
        json_data = {
            'title':data['title'],
            'date':data['date_published'],
            'article': data['article'],
            }
        input_text = json.dumps(json_data)
        
        res = get_embedding(input_text)
        hash = getHash(data['source'])
        
        index_name = 'blog-news-index'
        document = {
          'vector_field': res,
        }
        id = hash
    
        response = client.index(
            index = index_name,
            body = document,
            id = id,
            refresh = True
        )
        
    return 'SUCCESS'


def get_embedding(input_text, model="text-embedding-ada-002"):
    client = OpenAI(
        api_key=get_secret(),
        )
    
    response = client.embeddings.create(input = input_text, model=model)
    embeddings = response.data[0].embedding
    
    
    return embeddings

def getHash(string):
    result = hashlib.md5(string.encode())
    return result.hexdigest()

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
    
def getFromS3():
    try:
        # Put the object in the S3 bucket
        print("Starting S3...")
        response = client_s3.get_object(
        Bucket='rdsdataforos',
        Key='rdsdata',
        )
        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading object: {str(e)}')
        }