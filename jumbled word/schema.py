import boto3
import os
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
load_dotenv()

print('dynamodb connected!!....')

dynamodb = boto3.resource(service_name=os.getenv('service_name'), region_name=os.getenv(
    'region_name'), aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))
existing_tables = [table.name for table in dynamodb.tables.all()]

engagement = os.environ.get('JumbledWord_Engagement', 'TB_JumbledWord_Engagement')
uPoints = os.environ.get('User_Points', 'TB_User_Points')
session = os.environ.get('Temp_JumbledWord_Session', 'TB_Temp_JumbledWord_Session')
jBank = os.environ.get('JumbledWord_bank', 'TB_JumbledWord_bank')

# uMaster = os.environ.get('User_Master', 'TB_User_Master')
# tMaster = os.environ.get('Telegram_Master', 'TB_Telegram_Master')


if engagement not in existing_tables:
    dynamodb.create_table(
        TableName = engagement,
        KeySchema=[
            {
                'AttributeName': 'Date',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'Datetime',
                'KeyType': 'RANGE'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Datetime',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    print('create table JumbledWord_Engagement')


# if uMaster not in existing_tables:
#     dynamodb.create_table(
#         TableName=uMaster,
#         KeySchema=[
#             {
#                 'AttributeName': 'User_id',
#                 'KeyType': 'HASH'  # Partition key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'User_id',
#                 'AttributeType': 'S'
#             }
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 10,
#             'WriteCapacityUnits': 10
#         }
#     )
#     print('create table User_Master')

if uPoints not in existing_tables:
    dynamodb.create_table(
        TableName=uPoints,
        KeySchema=[
            {
                'AttributeName': 'User_id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'User_id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    print('create table User_Points')

# if tMaster not in existing_tables:
#     dynamodb.create_table(
#         TableName=tMaster,
#         KeySchema=[
#             {
#                 'AttributeName': 'User_id',
#                 'KeyType': 'HASH'  # Partition key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'User_id',
#                 'AttributeType': 'S'
#             }
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 10,
#             'WriteCapacityUnits': 10
#         }
#     )
#     print("Table status: Telegram_Master")

# print('Hello Temp_JumbledWord_Session table id. we need for that we need to generate the Id!! you need to genarate the id.!!!!!!!!!!!!')
print(existing_tables, '-----------------')
if session not in existing_tables:
    dynamodb.create_table(
        TableName=session,
        KeySchema=[
            {
                'AttributeName': 'ID',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ID',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
if jBank not in existing_tables:
    dynamodb.create_table(
        TableName=jBank,
        KeySchema=[
            {
                'AttributeName': 'word',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'word',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
