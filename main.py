import openpyxl
import pandas as pd
import time
import datetime
import sys
import os
import math
import requests
import re
import random
import datetime
import json
import requests
import pprint
import base64

def get_auth(code):

    sitename = 'xFIxyfnGKCzAJWefphKxEV:Yc2QCaPWAd2pDJo9YBxZiC'
    sitename_bytes = sitename.encode('ascii')
    sitename_base64 = base64.b64encode(sitename_bytes)
    sitename_base64_str = sitename_base64.decode('ascii')

    url = "https://lmk4100.cafe24api.com/api/v2/oauth/token"
    payload = '''grant_type=authorization_code&code={}&redirect_uri=https://lmk4100.cafe24.com'''.format(code)
    headers = {
        'Authorization': "Basic {}".format(sitename_base64_str),
        'Content-Type': "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print("get_auth:",response.text)
    result=json.loads(response.text)

    with open('token.json', 'w') as f:
        json.dump(result, f, indent=2)

def get_token_from_fresh_token(refresh_token):
    sitename = 'xFIxyfnGKCzAJWefphKxEV:Yc2QCaPWAd2pDJo9YBxZiC'
    sitename_bytes = sitename.encode('ascii')
    sitename_base64 = base64.b64encode(sitename_bytes)
    sitename_base64_str = sitename_base64.decode('ascii')

    with open('token.json', 'r') as f:
        json_data = json.load(f)

    refresh_token=json_data['refresh_token']

    url = "https://lmk4100.cafe24api.com/api/v2/oauth/token"
    payload = '''grant_type=refresh_token&refresh_token={}'''.format(refresh_token)
    headers = {
        'Authorization': "Basic {}".format(sitename_base64_str),
        'Content-Type': "application/x-www-form-urlencoded"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    result = json.loads(response.text)
    print("get_token_from_refresh_token",response.text)

    with open('token.json', 'w') as f:
        json.dump(result, f, indent=2)

def get_memo(access_token,product_no):
    url = "https://lmk4100.cafe24api.com/api/v2/admin/products/{}/memos".format(product_no)
    headers = {
        'Authorization': "Bearer {}".format(access_token),
        'Content-Type': "application/json",
        'X-Cafe24-Api-Version': "2023-03-01"
        }
    response = requests.request("GET", url, headers=headers)
    # print(response.text)
    result=json.loads(response.text)
    print("get_memo:",response.text)
    return result

def get_product_info(access_token,product_no):
    url = "https://lmk4100.cafe24api.com/api/v2/admin/products/{}".format(product_no)
    headers = {
        'Authorization': "Bearer {}".format(access_token),
        'Content-Type': "application/json",
        'X-Cafe24-Api-Version': "2023-03-01"
    }
    response = requests.request("GET", url, headers=headers)
    # print(response.text)
    result=json.loads(response.text)
    print("get_product_info:",response.text)
    return result

def get_nft_info(collection,name):

    url = "https://data-api.nftgo.io/eth/v1/collection/{}/filtered_nfts?sort_by=listing_price_high_to_low&is_listing=true&offset=0&limit=20".format(collection)

    headers = {
        "accept": "application/json",
        "X-API-KEY": "bbf39436-0723-41fc-b95d-7dfe87bab701"
    }
    response = requests.get(url, headers=headers)
    # print(response.text)

    results=json.loads(response.text)['nfts']
    price=0
    for result in results:

        target_name=result['name']
        # print(target_name)
        try:
            listing_price=result['listing_price']['value']
        except:
            print("가격없음")
            pprint.pprint(result)
            listing_price=0
            price=0

        if target_name.find(name)>=0:
            price=listing_price
            break
        # print("--------------------------------")
    return price

def change_price(product_no,price,access_token):
    url = "https://lmk4100.cafe24api.com/api/v2/admin/products/{}".format(product_no)
    # payload = f'''{
    #     "shop_no": 1,
    #     "request": {
    #         "price": {price},
    #     }
    # }'''
    # price=str(price)
    payload=json.dumps({"shop_no":1,"request":{"price":price}})
    headers = {
        'Authorization': "Bearer {}".format(access_token),
        'Content-Type': "application/json",
        'X-Cafe24-Api-Version': "2023-03-01"
    }
    response = requests.request("PUT", url, data=payload, headers=headers)
    print("change_price",response.text)

with open('token.json', 'r') as f:
    json_data = json.load(f)

#인증정보 얻어오기
refresh_token=json_data['refresh_token']
print(refresh_token)
get_token_from_fresh_token(refresh_token)
with open('token.json', 'r') as f:
    json_data = json.load(f)
access_token=json_data['access_token']
print(access_token)


#상품별 정보 얻어오기

data_list=list(pd.read_csv('list.csv')['상품번호'])
print(data_list)
for index,product_no in enumerate(data_list):
    print("{}번째 동기화중...".format(index+1))
    if index%100==0 and index>=1:
        with open('token.json', 'r') as f:
            json_data = json.load(f)
        # 인증정보 얻어오기
        refresh_token = json_data['refresh_token']
        print(refresh_token)
        get_token_from_fresh_token(refresh_token)
        with open('token.json', 'r') as f:
            json_data = json.load(f)
        access_token = json_data['access_token']
        print(access_token)

    time_now=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("time:",time_now)
    try:
        memo=get_memo(access_token,product_no)
        contracts = memo['memos'][0]['memo']

    except:
        print("접속POOL1")
        time.sleep(60)
        continue
    time.sleep(0.6)

    try:
        product_info=get_product_info(access_token,product_no)
        collection = product_info['product']['product_name'].split("_")[0]
        name = product_info['product']['product_name'].split("_")[-1]
        print('product_no:', product_no)
        print('contracts:', contracts)
        print("collection:", collection)
        print('name:', name)
    except:
        print("접속 POOL2")
        time.sleep(60)
        continue
    time.sleep(0.6)

    try:
        price=get_nft_info(contracts,name)
        print('price:', price)

    except:
        print("접속POOL3")
        time.sleep(60)
        continue

    try:
        change_price(product_no, price, access_token)
    except:
        print("접속POOL4")
        time.sleep(60)
        continue

    print("=============================")
    time.sleep(0.6)



