import http.client
import urllib.parse 
import json
import boto3
import operator
import sys
from random import randint
from time import sleep
from botocore.vendored import requests

API_KEY = 'd7d57a7d3bf8485abf873f3f95a8e61b'
API_ENDPOINT = ''

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
        
    text = str(get_text(event["decryptedBucket"], event["decryptedKey"]))
    data = {'text': text}
    key = 'd7d57a7d3bf8485abf873f3f95a8e61b'


    params = {'lang': event['sourceLanguage'], 'mode': 'proof', 'text': text}

    host = 'api.cognitive.microsoft.com'
    path = '/bing/v7.0/spellcheck'
    print (text)
    headers = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        conn = http.client.HTTPSConnection(host)
        params = urllib.parse.urlencode (params)
        conn.request ("POST", path, params, headers)
        response = conn.getresponse ()
        js = json.loads(response.read())
        sleep(randint(1,10))
        if len(js['flaggedTokens']) != 0:
            for i in range(0,len(js['flaggedTokens'])):
                text = text.replace(js['flaggedTokens'][i]['token'],js['flaggedTokens'][i]['suggestions'][0]['suggestion'])
        print (text)
        #spellcheckKey = "spellcheck-"+event['decryptedKey']
        spellcheckKey = event['decryptedKey'] + "-spellcheck"
        s3.Bucket(event['decryptedBucket']).put_object(Key=spellcheckKey, Body=text, ACL='public-read', ContentType='text/plain')
        output = {
            "method": event['method'],
            "confidence": event['confidence'],
            "decryptedBucket": event['decryptedBucket'],
            "decryptedKey": spellcheckKey,
            "sourceLanguage": event['sourceLanguage']
            }
    except:
        print("Unexpected error:", sys.exc_info()[0])
        output = {
            "method": event['method'],
            "confidence": event['confidence'],
            "decryptedBucket": event['decryptedBucket'],
            "decryptedKey": event['decryptedKey'],
            "sourceLanguage": event['sourceLanguage']
        }
        return output
    return output
        


def get_text(bucket, key):
    """
    Retrieves the specified file in S3 containing the text output by the OCR module

    :param bucket: the S3 bucket
    :param key: the S3 key (file name)
    :return: a string containing the text
    """
    s3 = boto3.resource("s3")

    ocr_obj = s3.Object(bucket, key)
    response = ocr_obj.get()
    data = response["Body"].read().decode('utf-8') 

    return data
