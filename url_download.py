import json
import time
import hashlib
import boto3
from bs4 import BeautifulSoup 
import requests
from datetime import datetime
from botocore.exceptions import ClientError

client_ld = boto3.client('lambda')
client_table = boto3.client("dynamodb")

def lambda_handler(event, context):
    # TODO implement
    print("Starting....")
    try:
        response = client_table.get_item(
                    TableName='URLlookup',
                    Key={
                        'hashID': {'S':event['url']},
                        }
                    )
    except ClientError as e:
        raise e
    print("Looked up URL")
    #check if URL already visited
    if "Item" not in response:
        print("URL not visited")
        if event['site'] == 'hackernews':
            request = hackernews(event['url'])
        elif event['site'] == 'darkreading':
            request = darkreading(event['url'])
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('Unknown website')
            }
        
        response2 = invokeGptApi(request) #pass data to API
        
        try:
            response3 = client_table.put_item(
                TableName='URLlookup',
                Item={
                    "hashID": {'S': event['url']},
                    }
                )
        except ClientError as e:
            raise 
        
        return {
            'statusCode': 200,
            'body': json.dumps('URL passed to API')
        }
    else:
        print('URL already visited')
        return {
            'statusCode': 200,
            'body': json.dumps('URL already visited')
        }

'''
def hashURL(url):
    return str(hashlib.md5(url.encode('utf-8')).hexdigest())
'''

def hackernews(url):
    print("Getting content...", url)
    try:
        r = requests.get(url) 
    except Exception as e:
        print('Error: ', e)
    print("Content Received")
    soup = BeautifulSoup(r.content, 'html5lib')
    title = soup.find('h1', attrs = {'class':'story-title'}).a.text
    date = soup.find('span', attrs = {'class':'author'}).text
    imageURL = soup.find('div', attrs = {'class':'separator'}).a['href']
    #print(title)
    #print(date)
    #print(imageURL)
    table = soup.find('div', attrs = {'class':'articlebody clear cf'})
    sentences = []
    
    for row in table.find_all('p'):
        sentences.append(row.text)
    article = ' '.join(sentences)
    #print(article)
    date_parsed = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
    #print(date_parsed)
    input = {
        'title':title,
        'date':date_parsed,
        'imageURL':imageURL,
        'article':article,
        'source':url
    }
    print(input)
    return input
    

def darkreading(url):
    print("Getting content...")
    try:
        r = requests.get(url) 
    except Exception as e:
        print('Error: ', e)
    print("Content Received")
    soup = BeautifulSoup(r.content, 'html5lib')
    title = soup.find('h1', attrs = {'class':'ArticleBase-HeaderTitle'}).span.text
    date = soup.find('div', attrs = {'class':'Contributors-InfoWrapper'}).p.text
    imageURL = soup.find('div', attrs = {'class':'CaptionedContent-Content'}).img['src'].split('?')[0]
    #print(title)
    #print(date)
    #print(imageURL)
    table = soup.find('div', attrs = {'class':'ContentModule-Wrapper'})
    sentences = []
    
    for row in table.find_all('p'):
        sentences.append(row.text)
    #print(len(sentences))
    article = ' '.join(sentences)
    #print(article)
    date_parsed = datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
    #print(date_parsed)
    input = {
        'title':title,
        'date':date_parsed,
        'imageURL':imageURL,
        'article':article,
        'source':url
    }
    return input
    
def invokeGptApi(input):
    response = client_ld.invoke(
    FunctionName = 'arn:aws:lambda:us-east-2:689050894738:function:blog_gpt_api',
    InvocationType = 'Event',
    Payload = json.dumps(input)
    )
    return response