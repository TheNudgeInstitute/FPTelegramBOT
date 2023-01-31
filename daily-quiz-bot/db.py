from collections import defaultdict

import boto3
import os

from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Key

load_dotenv()


class Database:
    def __init__(self):
        self.dynamo_client = boto3.resource(service_name=os.getenv('AWS_SERVICE_NAME'),
                                            region_name=os.getenv('AWS_REGION_NAME'),
                                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        self.quiz_bank = self.dynamo_client.Table('TB_QuizBot_Bank')
        self.quiz_polls = self.dynamo_client.Table('TB_QuizBot_Polls')
        self.quiz_engagement = self.dynamo_client.Table('TB_QuizBot_Engagement')
        self.quiz_session = self.dynamo_client.Table('TB_QuizBot_Session')

    def get_quiz(self):
        response = self.quiz_bank.query(IndexName='quiz-index',
                                        KeyConditionExpression=Key('posted').eq(b'0'),
                                        ScanIndexForward=True,
                                        Limit=1)
        return response['Items'][0] if response else None

    def update_quiz(self, quiz):
        # Mark quiz as posted
        self.quiz_bank.update_item(Key={'quiz_no': quiz['quiz_no']},
                                   UpdateExpression='SET posted = :p',
                                   ExpressionAttributeValues={':p': b'1'})
        # Create quiz engagement
        n = len(quiz.get('questions'))
        engagement = {
            'quiz_no': quiz['quiz_no'],
            'timestamp': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
            'engagement': [0] * n,
            'correct_answers': [0] * n
        }
        self.quiz_engagement.put_item(Item=engagement)

    def add_poll(self, poll):
        self.quiz_polls.put_item(Item=poll)

    def get_active_polls(self):
        return self.quiz_polls.scan()['Items']

    def update_poll_status(self, poll):
        self.quiz_polls.delete_item(Key={'poll_id': poll['poll_id']})

    def get_poll(self, poll_id):
        response = self.quiz_polls.get_item(Key={'poll_id': poll_id})
        print(response)
        return response['Item']

    def update_quiz_engagement(self, quiz_no, question_no, score):
        question_index = question_no - 1
        update_expression = f'SET engagement[{question_index}] = engagement[{question_index}] + :val1, ' \
                            f'correct_answers[{question_index}] = correct_answers[{question_index}] + :val2'
        self.quiz_engagement.update_item(Key={'quiz_no': quiz_no},
                                         UpdateExpression=update_expression,
                                         ExpressionAttributeValues={':val1': 1, ':val2': score})

    def update_quiz_session(self, quiz_no, question_no, user, score):
        user_id = str(user.get('id'))
        response = self.quiz_session.get_item(Key={'quiz_no': quiz_no, 'user_id': user_id})
        if 'Item' not in response:
            # if user response does not exist for quiz
            session = {
                'quiz_no': quiz_no,
                'user_id': user_id,
                'user': user,
                'scores': [0] * 5
            }
            self.quiz_session.put_item(Item=session)

        question_index = question_no - 1
        self.quiz_session.update_item(Key={'quiz_no': quiz_no, 'user_id': user_id},
                                      UpdateExpression=f'SET scores[{question_index}] = :val',
                                      ExpressionAttributeValues={':val': score})

    def get_quiz_results(self, quiz_no):
        response = self.quiz_session.query(KeyConditionExpression=Key('quiz_no').eq(quiz_no))
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = self.quiz_session.query(KeyConditionExpression=Key('quiz_no').eq(quiz_no),
                                               ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        score_map = defaultdict(list)
        for item in items:
            total_score = sum(item['scores'])
            user = item['user']
            score_map[total_score].append(
                '@' + user.get('username') if user.get('username') else user.get('first_name', ''))
        return score_map
