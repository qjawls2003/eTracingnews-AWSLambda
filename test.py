import json
from bs4 import BeautifulSoup 
import requests
#import boto3
import html5lib

#client_ld = boto3.client('lambda')
urls = []
responseList = []
def lambda_handler():
    # TODO implement
    print("Starting...!")
    #populate the urls list
        
    #hackernews() 
    #darkreading()
    threatpost()
    resList = set()
    for url,site in urls: #invoke downloader async
        if url not in resList:
            input = {
                'url':url,
                'site':site
            }
            #res = invokeDownloader(input)
            resList.add(url)
            #responseList.append(res['Payload'])
    print(urls)
    #print("number of response: ", len(responseList))
    print("number of urls: ", len(urls))
    print(len(resList))
    return {
        'statusCode': 200,
        'body': json.dumps('Sent tasks to ')
    }

'''
def invokeDownloader(input):
    response = client_ld.invoke(
    FunctionName = 'arn:aws:lambda:us-east-1:689050894738:function:blog_download',
    InvocationType = 'RequestResponse',
    Payload = json.dumps(input)
    )
    return response
    #print(json.load(response['Payload']))
 '''   

def hackernews():
    URL = "https://thehackernews.com/"
    print('Getting URL content...')
    try:
        r = requests.get(URL) 
    except Exception as e:
        print('Error: ', )
    print('URL content...')
    soup = BeautifulSoup(r.content, 'html5lib')
    
    table = soup.find('div', attrs = {'class':'blog-posts clear'})
    for row in table.find_all_next('div', attrs = {'class':'body-post clear'}):
        urls.append((row.a['href'],'hackernews'))
    
def darkreading():
    URL = "https://www.darkreading.com"
    print('Getting URL content...')
    r = requests.get(URL) 
    print('URL content...')
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.find('div', attrs = {'class':'LatestFeatured-Content'})
    for row in table.find_all_next('div', attrs = {'class':'ListPreview-TitleWrapper'}):
        urls.append((URL + row.a['href'],'darkreading'))
    

def threatpost():
    URL = "https://cyberscoop.com/"
    print('Getting URL content...')
    r = requests.get(URL) 
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.find('article', attrs = {'class':'post-item'})
    for row in table.find_all_next('h3', attrs = {'class':'post-item__title'}):
        urls.append((row.a['href'],'cyberscoop'))

if __name__ == '__main__':
    lambda_handler()