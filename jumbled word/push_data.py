import boto3
import os
import csv
from dotenv import load_dotenv

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key")
)

dynamodb_client = session.client('dynamodb')

table_name = os.getenv("JumbledWord_Bank")
_id = 1
# Open the CSV file
with open('Telegram_DB_Data - Jumbled Word Bank(2).csv', 'r') as file:
    
    csv_data = csv.DictReader(file)
    
    # Loop through each row of the CSV data
    for row in csv_data:
        item = {
            'word': {'S': str(_id)}
        }
        if row['4L Word']:
            item['four_level_word'] = {'S': row['4L Word']}
        if row['4L_FLAG']:
            item['four_level_flag'] = {'S': row['4L_FLAG']}
        if row['5L word']:
            item['five_level_word'] = {'S': row['5L word']}
        if row['5L_FLAG']:
            item['five_level_flag'] = {'S': row['5L_FLAG']}
        if row['6L word']:
            item['six_level_word'] = {'S': row['6L word']}
        if row['6L_FLAG']:
            item['six_level_flag'] = {'S': row['6L_FLAG']}

        if len(item) > 1:
            
            dynamodb_client.put_item(TableName=table_name, Item=item)
            _id += 1




