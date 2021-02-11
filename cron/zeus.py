import os
import json
import time
import requests
from five9cron import settings
from azure.common import AzureException
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient

from requests.exceptions import ConnectionError
from socket import timeout

NOBLE_ZEUS_URL = settings.NOBLE_ZEUS_URL
NOBLE_ZEUS_USERNAME = settings.NOBLE_ZEUS_USERNAME
API_NOBLE_ZEUS_PW = settings.API_NOBLE_ZEUS_PW
BASEFIVE9 = settings.BASEFIVE9

def updateFive9Files():
    # rootPath = os.path.dirname(os.path.abspath(__file__))
    stores = getStores()
    sendAzureBlob(json.dumps(stores), 'stores.json')

    # blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=nowopticsassets;AccountKey=STrZUiNrX45MIjaJGPwRnOf4lz/fSVnp1tu50ZQO45KGYTknYmcBo2a0/KQaamhfCpp302UV41N4Xr4McuJEqw==;EndpointSuffix=core.windows.net", container_name="test", blob_name="storespython.json")
    # with open("/home/marketing/Documents/jsonpython.json", "wb") as my_blob:
    #    blob_data = blob.download_blob()
    #    print(blob_data.content_as_bytes())

    methods = ['GetStoreInformation', 'GetStoreDoctorComments', 'GetStoreExamRooms']

    for s in stores:
        for m in methods:
            storeNumber = s['StoreNumber']
            fname = storeNumber + '_' + m + '.json'
            data = getEndpointData(storeNumber, '', m)

            sendAzureBlob(json.dumps(data), fname)

    return True


def getStores():
    stores = getEndpointData('', 'info', 'GetStoreInformation')

    return stores

def sendAzureBlob(content, fname):
    cs = 'DefaultEndpointsProtocol=https;AccountName=nowopticsassets;AccountKey=STrZUiNrX45MIjaJGPwRnOf4lz/fSVnp1tu50ZQO45KGYTknYmcBo2a0/KQaamhfCpp302UV41N4Xr4McuJEqw==;EndpointSuffix=core.windows.net'
    container = 'test'

    #try:
    blob = BlobClient.from_connection_string(cs, container, fname)
    blob.upload_blob(content, overwrite=True)    
    #except AzureException:
    #    print('Error while trying to upload to azure file ' + fname)

def createFile(content, path):
    content = json.dumps(content)
    f = open(path, 'w+')
    f.write(content)
    f.close()

def getToken():
    token_url = NOBLE_ZEUS_URL + '/Account/Login?UserName=' + NOBLE_ZEUS_USERNAME + '&Password=' + API_NOBLE_ZEUS_PW
    headers = { 'content-type': 'application/json; charset=UTF-8' }
    r = requests.get(token_url, headers=headers)
    token = r.text[1:-1]

    return token

def getEndpointData(storeId, dtype, endpoint):
    try:
        data = None
        token = getToken()
        storeParam = '?StoreNumber='
        requestType = endpoint

        if storeId != '' and storeId is not None and dtype != 'info':
            storeParam = '?StoreNumber=' + storeId
            
        finalEndpoint = NOBLE_ZEUS_URL + '/' + BASEFIVE9 + '/' + requestType + storeParam
        response = requests.get(finalEndpoint, headers=getConfig(token, NOBLE_ZEUS_USERNAME))
        data = response.text

        if response.status_code != 200 or data is None:
            time.sleep(3)
            getEndpointData(storeId, dtype, endpoint)
        
        return json.loads(data)
    except ConnectionError:
        time.sleep(3)
        getEndpointData(storeId, dtype, endpoint)
    except timeout:
        time.sleep(3)
        getEndpointData(storeId, dtype, endpoint)


def prependZeros(storeId):
    if (storeId < 10):
        return '000' + str(storeId)

    if(storeId < 100):
        return '00' + str(storeId)

    if(storeId < 1000):
        return '0' + str(storeId)

    return str(storeId)

def getConfig(token, username):
    return { 'Authorization': 'Bearer ' + token + ':' + username,
        'content-type': 'application/json', 
        'charset': 'utf-8' 
    }