import boto3
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.dynamo_client = boto3.resource(service_name=os.getenv('AWS_SERVICE_NAME'),
                                            region_name=os.getenv('AWS_REGION_NAME'),
                                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    def send_data(self, data, table_name):
        table = self.dynamo_client.Table(table_name)
        table.put_item(Item=data)

    def get_prompts(self):
        table = self.dynamo_client.Table("TB_StoryBuilding_Bank")
        response = table.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return [item.get('prompt') for item in data]
