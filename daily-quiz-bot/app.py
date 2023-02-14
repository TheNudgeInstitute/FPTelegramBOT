import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from db import Database
from bot import send_poll, stop_poll, send_message
from update import process_updates

app = Flask(__name__)
DB = Database()


@app.route('/')
def hello_world():
    return 'English Quiz Bot is running'


@app.route('/start-quiz', methods=['GET'])
def start_quiz():
    with app.app_context():
        quiz = DB.get_quiz()
        if quiz is None:
            return 'no quiz found', 422
        questions = quiz.get('questions')
        if questions is not None:
            send_message("Hey Jobcoachers, here is your quiz for today!")
        for index, question in enumerate(questions, start=1):
            prompt = f"Question [{index}/{len(questions)}]: {question.get('prompt')}"
            result = send_poll(prompt,
                               question.get('options'),
                               question.get('correct_option_id'),
                               question.get('explanation'))
            poll = {
                'poll_id': result.get('poll').get('id'),
                'message_id': result.get('message_id'),
                'correct_option_id': question.get('correct_option_id'),
                'quiz_no': quiz.get('quiz_no'),
                'question_no': index
            }
            DB.add_poll(poll)
        DB.update_quiz(quiz)
        quiz_expiration_time = float(os.environ.get('QUIZ_EXPIRATION', 10))
        scheduler.add_job(end_quiz,
                          trigger='date',
                          run_date=datetime.now() + timedelta(hours=quiz_expiration_time),
                          args=[quiz.get('quiz_no')])
        return f"started quiz {quiz.get('quiz_no')}", 200


scheduler = BackgroundScheduler()
# Start a new quiz every day at 4:00 PM IST
scheduler.add_job(start_quiz,
                  trigger='cron',
                  hour=os.environ.get('QUIZ_START_HOUR', 10),
                  minute=os.environ.get('QUIZ_START_MINUTE', 30))
scheduler.start()


@app.route('/stop-quiz', methods=['PUT'])
def stop_quiz():
    return end_quiz(int(request.args.get('quiz_no')))


def end_quiz(quiz_no):
    with app.app_context():
        print("ending quiz", quiz_no)
        polls = DB.get_active_polls()
        poll_map = {poll['poll_id']: poll for poll in polls}

        for poll in polls:
            stop_poll(poll.get('message_id'))
        process_poll_answers(poll_map, quiz_no)

        for poll in polls:
            DB.update_poll_status(poll)
        print("ended quiz", quiz_no)
        return leaderboad(quiz_no)


def process_poll_answers(poll_map, quiz_no):
    updates = process_updates()
    engagement, correct_answers = [0] * 5, [0] * 5
    user_answers = dict()

    for update in updates:
        try:
            poll_answer = update['poll_answer']
            poll = poll_map[poll_answer.get('poll_id')]

            selected_option = poll_answer.get('option_ids')[0]
            score = int(poll.get('correct_option_id') == selected_option)  # 1 or 0

            question_index = int(poll['question_no'] - 1)
            engagement[question_index] += 1
            correct_answers[question_index] += score

            user_id = str(poll_answer.get('user').get('id'))
            if user_id not in user_answers:
                user_answers[user_id] = {
                    'scores': [None] * 5,
                    'user': poll_answer.get('user')
                }
            user_answers[user_id]['scores'][question_index] = score
        except Exception as e:
            print(e)

    DB.put_quiz_engagement(quiz_no, engagement, correct_answers)
    DB.put_quiz_session(quiz_no, user_answers)


@app.route('/send-leaderboard', methods=['GET'])
def send_leaderboard():
    quiz_no = int(request.args.get('quiz_no'))
    return leaderboad(quiz_no)


def leaderboad(quiz_no):
    score_map = DB.get_quiz_results(quiz_no)

    five = " ".join(score_map.get(5, []))
    four = " ".join(score_map.get(4, []))
    three = " ".join(score_map.get(3, []))
    text = f"Thank you for participating in today's Daily Quiz! 🥳🎉🎉🎉\n\n" \
           f"🥇 Jobcoachers who got 5/5 Questions correct ⭐⭐⭐⭐⭐:\n" \
           f"{five}\n\n" \
           f"🥈 Jobcoachers who got 4/5 Questions correct ⭐⭐⭐⭐:\n" \
           f"{four}\n\n" \
           f"🥉 Jobcoachers who got 3/5 Questions correct ⭐⭐⭐:\n" \
           f"{three}\n\n" \
           f"Congratulations Jobcoachers! 👏🎊" \
           f"Keep it up and practice more. 📚"
    send_message(text)
    print(text)
    return text, 200


if __name__ == '__main__':
    print("Started English Quiz Bot")
    app.run()
