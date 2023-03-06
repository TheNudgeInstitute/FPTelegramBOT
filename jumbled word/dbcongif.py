import boto3
import os
from dotenv import load_dotenv
import pandas as pd
from boto3.dynamodb.conditions import Key, Attr

load_dotenv()  # this is for the env file loading

Session_id = 0

class DynamoDB_con():
    def __init__(self):
        self.dynamo_client = boto3.resource(service_name=os.getenv('service_name'), region_name=os.getenv(
            'region_name'), aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))

    def send_data(self, data, tableName):
        db = self.dynamo_client.Table(tableName)
        db.put_item(Item=data)
        print('Data is sending to the database!!!!')
        
    

    def read_read(self, tableName):
        table = self.dynamo_client.Table(tableName)
        response = table.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        # print('total out put data: ',data)
        return data, len(data)
        
        return data, len(data)
    def update_all_values(self,word,flag):
        table = self.dynamo_client.Table(os.getenv("JumbledWord_Bank"))
        query_params = {
            'FilterExpression': Attr(flag).eq('Y'),
            'ProjectionExpression': f'word,{word}',
            
        }

        
        query_result = table.scan(**query_params)

        word_id = []
        for item in query_result['Items']:
            word_id.append(item['word'])
            
        for i in range (len(word_id)):
            partition_key_value = {'word':word_id[i]}
            response = table.update_item(
                Key=partition_key_value,
                UpdateExpression=f'set {flag} = :val',
                ExpressionAttributeValues={':val': 'N'}
            )

        print(response)
        
        
    def get_words(self,word,flag):
        table = self.dynamo_client.Table(os.getenv("JumbledWord_Bank"))
        
        query_params = {
            'FilterExpression': Attr(flag).eq('N'),
            'ProjectionExpression': f'word,{word}',
            # 'Limit':3
        }

        
        query_result = table.scan(**query_params)

        
        return query_result['Items'][0]
    
    def update_flag(self,_id,flag):
        table = self.dynamo_client.Table(os.getenv("JumbledWord_Bank"))
        response = table.update_item(Key={'word': _id },UpdateExpression=f'SET {flag} = :val1',ExpressionAttributeValues={':val1': 'Y' })

        print(response)
        print(f"Flag has been updated for Key: {_id} and flag: {flag}")



