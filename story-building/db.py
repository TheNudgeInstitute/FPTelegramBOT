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
        self.storybuilding_bank = self.dynamo_client.Table(
            os.getenv('TABLE_STORYBUILDING_BANK', 'TB_StoryBuilding_Bank'))
        self.storybuilding_data = self.dynamo_client.Table(
            os.getenv('TABLE_STORYBUILDING_DATA', 'TB_StoryBuilding_Data'))

    def send_data(self, data):
        self.storybuilding_data.put_item(Item=data)

    def get_prompts(self):
        response = self.storybuilding_bank.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = self.storybuilding_bank.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return [item.get('prompt') for item in data]
