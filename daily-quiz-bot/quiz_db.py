import os
from datetime import datetime

from flask import current_app, g
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = PyMongo(current_app, os.environ.get('MONGO_QUIZ_URI')).db
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def get_quiz():
    # get one unused quiz
    return db.quiz_bank.find_one({'used': None}, sort=[('quiz_no', 1)])


def update_quiz(quiz):
    # update quiz to used
    db.quiz_bank.update_one({'_id': quiz.get('_id')}, {'$set': {
        'used': True,
        'posted': datetime.utcnow()
    }})
    # create entry for quiz engagement
    db.quiz_engagement.insert_one({
        'quiz_id': quiz.get('_id'),
        'quiz_no': quiz.get('quiz_no'),
        'date': datetime.utcnow(),
        'engagement': [0] * len(quiz.get('questions')),
        'correct_answers': [0] * len(quiz.get('questions'))
    })


def add_poll(poll):
    # save poll as a reference to a message
    db.polls.insert_one(poll)


def get_poll(poll_id):
    return db.polls.find_one({'poll_id': poll_id})


def update_quiz_engagement(quiz_id, question_no, score):
    # update the engagement and correct_answers index accordingly
    db.quiz_engagement.update_one(
        {
            'quiz_id': quiz_id
        },
        {
            '$inc': {
                'engagement.' + str(question_no - 1): 1,
                'correct_answers.' + str(question_no - 1): score
            }
        }
    )


def update_quiz_session(quiz_id, quiz_no, question_no, user, score):
    # update or create an answer object per user per quiz
    db.quiz_session.update_one(
        {
            'quiz_id': quiz_id,
            'user_id': user.get('id'),
            'quiz_no': quiz_no
        },
        {
            '$set': {
                'answer_' + str(question_no): score,
                'user': user
            },
            '$inc': {
                'quiz_score': score
            }
        },
        upsert=True
    )


def get_active_polls(quiz_no: int):
    return [poll for poll in db.polls.find({'quiz_no': quiz_no, 'active': True})]


def update_poll_status(quiz_no: int):
    db.polls.update_many(
        {
            'quiz_no': quiz_no,
            'active': True
        },
        {
            '$set':
                {
                    'stopped': datetime.utcnow(),
                    'active': False
                }
        },
        upsert=False)


def get_quiz_results(quiz_no: int):
    return [score for score in db.quiz_session.aggregate([
        {
            '$match': {
                'quiz_no': quiz_no
            }
        }, {
            '$group': {
                '_id': '$quiz_score',
                'users': {
                    '$push': '$user'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'total_score': '$_id',
                'users': 1
            }
        }
    ])]
