import json
import boto3
from botocore.exceptions import ClientError
import mysql.connector
from mysql.connector import Error
import sys
import logging
import os
from datetime import date

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_proxy_host = os.environ['RDS_PROXY_HOST']
db_name = os.environ['DB_NAME']

client_s3 = boto3.client('s3')

connection_config = {
    'host': rds_proxy_host,
    'user': user_name,
    'password': password,
    'database': db_name
}


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)
        
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
    res = getFromRDS()
    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }


def uploadTos3(input):
    try:
        # Put the object in the S3 bucket
        print("Starting S3...")
        response = client_s3.put_object(
        Body=input,
        Bucket='rdsdataforos',
        Key='rdsdata',
        ContentType='application/json'
        )
        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading object: {str(e)}')
        }
    

def getFromRDS():
    try:
        connection = mysql.connector.connect(**connection_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT * FROM blog_news_1.Articles"
            cursor.execute(query)
            rows = cursor.fetchall()
            field_names = [i[0] for i in cursor.description]
            # Convert rows to JSON format
            json_data = []
            for row in rows:
                json_row = dict(zip(field_names, row))
                json_data.append(json_row)

            # Convert the list to a JSON string
            json_string = json.dumps(json_data, indent=2, cls=DateEncoder)
            print('Retrieved Data (JSON):')
            print(len(json_data))
            res = uploadTos3(json_string)
            print(res)
            
    except Error as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit(1)
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
    