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
    res = uploadToRDS(event)
    return res
    
    
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