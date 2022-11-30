import os

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = PyMongo(current_app, os.environ.get('MONGO_QUIZ_URI')).db
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def get_quiz_questions(n):
    return [question for question in db.questions.find({'used': False}).limit(n)]


def update_question(question_id, poll_id, quiz_id):
    update = {'used': True, 'poll_id': poll_id, 'quiz_id': quiz_id}
    db.questions.update_one({'_id': question_id}, {'$set': update})


def add_poll(poll_id, correct_option_id, quiz_id):
    poll = {'poll_id': poll_id, 'correct_option': correct_option_id, 'quiz_id': quiz_id}
    db.polls.insert_one(poll)


def get_poll(poll_id):
    return db.polls.find_one({'poll_id': poll_id})


def add_answer(answer):
    db.answers.insert_one(answer)
