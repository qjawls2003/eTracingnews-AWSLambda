import json
import time
import hashlib
from bs4 import BeautifulSoup 
import requests
from datetime import datetime


def lambda_handler(event):
    # TODO implement
    print("Starting....")
    '''
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
        
        return response2
    else:
        print('URL already visited')
        return 'URL already visited'
    '''
    request = cyberscoop(event['url'])
    print(request)
        
    

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
    

def cyberscoop(url):
    print("Getting content...")
    try:
        r = requests.get(url) 
    except Exception as e:
        print('Error: ', e)
    print("Content Received")
    soup = BeautifulSoup(r.content, 'html5lib')
    title = soup.find('h1', attrs = {'class':'single-article__title'}).text.strip()
    date = soup.find('time').text
    imageURL = soup.find('figure', attrs = {'class':'single-article__cover'}).img['src'].split('?')[0]
    #print(title)
    #print(date)
    #print(imageURL)
    table = soup.find('div', attrs = {'class':'single-article__content-inner has-drop-cap'})
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

if __name__ == '__main__':
    lambda_handler({'url':'https://cyberscoop.com/russia-hacktivist-noname-github-ddos/', 'site':'cyberscoop'})