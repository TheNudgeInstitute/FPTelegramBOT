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
        self.quiz_bank = self.dynamo_client.Table(os.getenv('TABLE_QUIZBOT_BANK', 'TB_QuizBot_Bank'))
        self.quiz_polls = self.dynamo_client.Table(os.getenv('TABLE_QUIZBOT_POLLS', 'TB_QuizBot_Polls'))
        self.quiz_engagement = self.dynamo_client.Table(os.getenv('TABLE_QUIZBOT_ENGAGEMENT', 'TB_QuizBot_Engagement'))
        self.quiz_session = self.dynamo_client.Table(os.getenv('TABLE_QUIZBOT_SESSION', 'TB_QuizBot_Session'))

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

    def add_poll(self, poll):
        self.quiz_polls.put_item(Item=poll)

    def get_active_polls(self):
        response = self.quiz_polls.scan()
        return response['Items'] if 'Items' in response else []

    def update_poll_status(self, poll):
        self.quiz_polls.delete_item(Key={'poll_id': poll['poll_id']})

    def put_quiz_engagement(self, quiz_no, engagement, correct_answers):
        timestamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        engagement = {
            'quiz_no': quiz_no,
            'timestamp': timestamp.isoformat(),
            'engagement': engagement,
            'correct_answers': correct_answers,
            'date': timestamp.strftime('%Y-%m-%d')
        }
        self.quiz_engagement.put_item(Item=engagement)

    def put_quiz_session(self, quiz_no, user_answers):
        timestamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        sessions = list()
        for user_id, user_answer in user_answers.items():
            sessions.append({
                'quiz_no': quiz_no,
                'user_id': user_id,
                'user': user_answer.get('user'),
                'scores': user_answer.get('scores'),
                'date': timestamp.strftime('%Y-%m-%d')
            })

        with self.quiz_session.batch_writer() as batch:
            for session in sessions:
                batch.put_item(Item=session)

    def get_quiz_results(self, quiz_no):
        response = self.quiz_session.query(KeyConditionExpression=Key('quiz_no').eq(quiz_no))
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = self.quiz_session.query(KeyConditionExpression=Key('quiz_no').eq(quiz_no),
                                               ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        score_map = defaultdict(list)
        for item in items:
            total_score = sum(filter(None, item['scores']))
            user = item['user']
            score_map[total_score].append(
                '@' + user.get('username') if user.get('username') else user.get('first_name', ''))
        return score_map
