import threading
import time
import datetime
import os
import time
import telebot
from datetime import date
import schedule
import random

# ___ import files
import common
from DB_class import DynamoDB_con
from dotenv import load_dotenv
import schema
import end_call

DB = DynamoDB_con()
load_dotenv()  # loading the env file

common.game_creater = {}
common.participants = []
common.scour_Dict = {}
common.red_scour = {}


game_time = datetime.datetime.now()
common.nextEditButton = None
common.last_Right_ans = ''

schedule.every().day.at("01:00").do(end_call.UpdateTheData)
schedule.run_all()


def restartGame():
    common.joinFlag = True  # to block joining patrticipants after 60 seconds
    common.chat_type = None
    common.gameCounter = 0
    common.game_creater = {}
    common.participants = []
    common.nextButtonCount = False
    common.nextEditButton = None
    common.editJoinMsg = None
    common.last_Right_ans = ''
    common.nextFlag = False  # show or hide next button
    common.total_players = 0
    common.time_breaker = False
    common.wait60sec = 0  # waiting time for particiants to join the game (60)
    common.wait40sec = 40  # waiting time for particiants to join the game (60
    common.guessTime = 40  # waiting time to guess the word
    # variiiii
    common.sec60 = 60
    common.word = ''
    common.used_words = []
    common.scour_Dict = {}
    common.runner = 0
    common.red_scour = {}
    common.gameStarted = False  # to block creating new game if one is going on


def ErrorHandler(er):
    restartGame()
    bot.send_message(common.chat_id, f'''Server is down try again start the game /jumbleword{os.getenv("bot_username")} \n  {er}''',
                     parse_mode='markdown'
                     )

def delete_message(chat_id, message_id, sec=0):
    # time.sleep(sec)
    bot.delete_message(chat_id, message_id)
    # return True

def controleNextBtn(message, bool):
    if common.gameCounter <= 10:
        try:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(telebot.types.InlineKeyboardButton(
                'Next Word', callback_data='next-jumble-word'),)
            common.time_breaker = True
            if (bool):
                common.nextEditButton = bot.send_message(
                    message.chat.id, f'Congratulations *{message.from_user.first_name}*👏🥳🎉, \nYou guessed the word',
                    disable_notification=True,
                    parse_mode='markdown')
                common.runner = 3

                common.scour_Dict[message.from_user.id]['points'] += 2
                if message.from_user.id in common.red_scour:
                    del common.red_scour[message.from_user.id]

                for std in common.red_scour:
                    if std in common.scour_Dict:
                        common.scour_Dict[std]["points"] += 1

                common.last_Right_ans = message.from_user.first_name
                common.time_breaker = True
                time.sleep(1)
                common.nextFlag = True
                if common.gameCounter == 10:
                    common.runner = 3

                    common.time_breaker = False

                    threads = threading.Thread(target=common.start_timer, args=(
                        'ques-wait', 1, 'join-jumble', message))
                    common.word = ''
                    try:
                        threads.start()
                    except Exception as e:
                        ErrorHandler(e)
                else:
                    join_game('join-jumble', message, 'gg', 0)
            else:
                if common.gameCounter == 10:
                    common.runner = 3
                    common.time_breaker = False

                    threads = threading.Thread(target=common.start_timer, args=(
                        'ques-wait', 1, 'join-jumble', message))
                    common.word = ''
                    try:
                        threads.start()
                    except Exception as e:
                        ErrorHandler(e)
                else:
                    common.nextEditButton = bot.send_message(
                        common.chat_id, f"Oops.. you ran out of time. 🕐🕑🕒\n Hey, word was: {common.gessWord}\nClick the button below for the next word 👇",
                        disable_notification=True,
                        reply_markup=keyboard,
                        parse_mode='markdown')
                    common.runner = 3
                    common.nextButtonCount = False
                    common.time_breaker = False

                    threads = threading.Thread(target=common.start_timer, args=(
                        'ques-wait', common.wait40sec, 'join-jumble', message)).start()

        except Exception as e:
            ErrorHandler(e)


def alert(messageId, msg, show_alert=False):
    if show_alert:
        bot.answer_callback_query(messageId, msg, show_alert=True)
    else:
        bot.answer_callback_query(messageId, msg)


def genrate_sessionId():
    sessionData, totalSess = DB.read_read('TB_Temp_JumbledWord_Session')
    f = True

    def generateFun():
        common.sessionId = random.randrange(1000, 9999)
        for dic in sessionData:
            print('dic: ', dic)
            if common.sessionId == dic['sessionId']:
                f = False
                break
    while True:
        print('while:True')
        generateFun()
        if f:
            break


def create_game(game, message, t=60):
    keyboard = telebot.types.InlineKeyboardMarkup()
    chat_id = message.chat.id
    common.chat_id = chat_id
    print('/jumbleword'+os.getenv("bot_username"),)
    if (game == '/jumbleword' or game == '/jumbleword'+os.getenv("bot_username")):
        print('----> inside create game ')
        keyboard.row(
            telebot.types.InlineKeyboardButton(text='Join Game 🎮', callback_data='join-jumble', activeforeground="red", activebackground="pink", pady=10),)
        first_name = message.from_user.first_name
        common.editJoinMsg = bot.send_message(
            chat_id, f'A Jumble word game is Start... \nYou Have  *⌛{t}* _s_ to Join',
            reply_markup=keyboard,
            parse_mode='markdown'
        )
        if t == common.sec60:
            bot.send_message(
                chat_id, f"Let's start ⏳\nThis game will have 10 rounds",
                parse_mode='markdown'
            )
            genrate_sessionId()
            bot.send_message(
                chat_id, f'{first_name} joined. \n There is now {common.total_players} players')
            common.scour_Dict[message.from_user.id] = {
                'points': 0, "user_name": message.from_user.first_name, 'sessionId': common.sessionId}
            # # creating thread for counter. students will get 60 seconds time to participate in jumble word game
            join_counter = threading.Thread(target=common.start_timer, args=(
                'join-wait', t, 'join-jumble', common.editJoinMsg))  # joining button thread
            try:
                join_counter.start()
            except Exception as e:
                ErrorHandler(e)


def auto_next_word(message):
    common.nextButtonCount = True  # for limiting the next button click
    common.time_breaker = True
    common.nextFlag = True
    join_game('join-jumble', "option", 'skip', 0)


def join_game(game, message, mode='auto', time=60):
    skip = False
    if mode == 'skip':
        skip = True

    elif mode == 'mannual':
        chat_id = message.json['message']['chat']['id']
    else:
        chat_id = message.json['chat']['id']
    if not (skip):
        global current_word_Message
        user_id = message.from_user.id
        if (game == 'join-jumble'):
            first_name = message.from_user.first_name

            if time == 0 and len(common.scour_Dict) == 1:
                bot.send_message(
                    chat_id, f'You need atleast 2 players to play this game !! \n \n \t Happy learning⬇',
                    parse_mode='markdown'
                )
                # resetting all the valiables to default
                restartGame()
            elif time == 0 and common.gameCounter < 10:
                common.time_breaker = True
                if mode == 'auto':
                    bot.send_message(
                        chat_id, f'Here is the first word ⬇',
                        disable_notification=True,
                        parse_mode='markdown'
                    )
                data = {"Datatime": str(datetime.datetime.now()), 'JumbledWord_InitiatedByUser_ID': str(
                    common.game_creater['InitiatedBy']), "JumbledWord_Participation": len(common.participants)}

                DB.send_data(data, 'TB_JumbledWord_Engagement')

                if common.runner == 0 or common.runner == 3:

                    current_word_Message = bot.send_message(
                        chat_id, str(common.gameCounter + 1) +
                        ") "+common.get_jumble(),
                        disable_notification=True,
                        parse_mode='markdown'
                    )
                    common.time_breaker = False
                    guessWait = threading.Thread(
                        target=common.start_timer, args=('guess-wait', common.guessTime, 'join-jumble', message))
                    try:
                        guessWait.start()
                    except Exception as e:
                        ErrorHandler(e)
            elif time > 0:
                if common.wait60sec <= 0:
                    alert(message.id,
                          "Game is already started! Try joining next game ")

                elif user_id in common.participants:
                    alert(message.id, 'you already joined :)')
                else:
                    common.total_players += 1
                    common.participants.append(user_id)
                    bot.send_message(
                        chat_id, f'{first_name} joined. \n There are now {common.total_players} players')
                    common.scour_Dict[message.from_user.id] = {
                        'points': 0, "user_name": message.from_user.first_name, 'sessionId': common.sessionId}
            elif common.gameCounter >= 10:
                common.time_breaker = False
                winner_announce = threading.Thread(
                    target=common.start_timer, args=(
                        'ques-wait', 1, 'join-jumble', message))
                try:
                    winner_announce.start()
                except Exception as e:
                    ErrorHandler(e)
    else:
        controleNextBtn(message, False)


def winner(message, r=True):
    common.time_breaker = True
    print('running')
    if r:
        chat_id = message.json['chat']['id']
    else:
        chat_id = common.chat_id

    print('total score!! : ', common.scour_Dict)
    li = []
    name = []
    for ele in common.scour_Dict:
        li.append(common.scour_Dict[ele]['points'])
        name.append(common.scour_Dict[ele]['user_name'])

    li2 = li.copy()
    li.sort(reverse=True)
    print(li, li2, name)

    firs = li2.index(li[0])
    first_name = name[li2.index(li[0])]
    li.pop(0)

    common.runner = 2
    if li2[firs] != 0:
        if len(common.scour_Dict) >= 2:
            sec = li2.index(li[0])
            sec_name = name[li2.index(li[0])]
            li.pop(0)
            if len(common.scour_Dict) >= 3:
                thd = li2.index(li[0])
                thd_name = name[li2.index(li[0])]
                li.pop(0)
                bot.send_message(chat_id, f''' Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉

                🥇 {first_name} got {li2[firs]//2}/{common.gameCounter} Questions correct ⭐️⭐️⭐️

                🥈 {sec_name} got {li2[sec]//2}/{common.gameCounter} Questions correct ⭐️⭐️

                🥉 {thd_name} got {li2[thd]//2}/{common.gameCounter} Questions correct ⭐️

                Congratulations {first_name} 👏🎊Keep it up and practice more. 📚📚📚''',
                                 disable_notification=True,
                                 parse_mode='markdown')
            else:
                bot.send_message(chat_id, f''' Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉

                🥇 {first_name} got {li2[firs]//2}/{common.gameCounter} Questions correct ⭐️⭐️⭐️

                🥈 {sec_name} got {li2[sec]//2}/{common.gameCounter} Questions correct ⭐️⭐️

                Congratulations {first_name} 👏🎊Keep it up and practice more.!! 📚📚📚''',
                                 disable_notification=True,
                                 parse_mode='markdown')
        else:
            bot.send_message(chat_id, f''' Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉

                🥇 {first_name} got {li2[firs]//2}/{common.gameCounter} Questions correct ⭐️⭐️⭐️

                Congratulations {first_name} 👏🎊Keep it up and practice more.!! 📚📚📚''',
                             disable_notification=True,
                             parse_mode='markdown')
            print('ddddddddddsssssssssssssss#####')
    else:
        bot.send_message(chat_id, f''' Thank you for participating in today's  Jumble word Game!
                  👎🏻👎🏻👎🏻Oops there is no Winner! 👎🏻👎🏻👎🏻 
            Try to answer it and practice more. 📚📚📚''',
                         disable_notification=True,
                         parse_mode='markdown')

    for d in common.scour_Dict:
        t = time.time()
        t_ms = int(t * 1000)
        data = {"Id": str(t_ms), "Datetime": str(datetime.datetime.now()), "User_Id": str(
            d), "Points_Scored": str(common.scour_Dict[d]['points']), "sessionId": common.scour_Dict[d]['sessionId']}
        DB.send_data(data, 'TB_Temp_JumbledWord_Session')
    today = str(date.today())
    print('one time run in a one day!!', today == common.todayDate)
    if today == common.todayDate:
        print(today)
        end_call.UpdateTheData()
        common.todayDate = today
    # resetting all the valiables to default
    restartGame()


print("Hi, Jumble here!\n\t", os.getenv('bot_username'))
bot = telebot.TeleBot(os.getenv('API_KEY'))


def main():
    @bot.message_handler(commands=['jumbleword'])
    def send_welcome(message):
        command = message.text
        print(message.chat.type, '-> chat type', command)
        if command.startswith('/jumbleword') and not common.gameStarted:
            # storing game creator information
            if common.joinFlag:
                common.total_players += 1
                common.game_creater = {
                    "date": game_time,
                    "InitiatedBy": message.from_user.id,
                    "total_common.participants": 0
                }
                common.participants.append(message.from_user.id)
                common.joinFlag = False
                common.gameStarted = True
                create_game(command, message)

    @bot.message_handler(content_types=['text'])
    def send_welcome(message):
        msg = message.text
        print(msg, common.word)
        keyboard = telebot.types.InlineKeyboardMarkup()
        try:
            if message.from_user.id not in common.scour_Dict.keys():
                alert(message.id, 'You are not a part of this game!')
        except:
            pass
        else:
            print('count', common.gameCounter)
            # if common.wait60sec == 0 or common.wait60sec == 1:
            #     common.word = ''
            if common.wait60sec > 1:
                if (msg.upper() == common.word):
                    common.word = ''
                    common.time_breaker = True
                    time.sleep(1)
                    controleNextBtn(message, True)

                elif (len(msg.upper()) == len(common.word)):
                    dic, dic2, bool = {}, {}, True
                    for i in range(len(msg.upper())):
                        if common.word[i] not in dic2:
                            dic2[common.word[i]] = 1
                        else:
                            dic2[common.word[i]] += 1

                        if msg.upper()[i] not in dic:
                            dic[msg.upper()[i]] = 1
                        else:
                            dic[msg.upper()[i]] += 1
                    try:
                        for k in dic:
                            if dic[k] != dic2[k]:
                                bool = False
                                break
                        if (bool):
                            bot.send_message(
                                message.json['chat']['id'], f'You got this just missed, try again {message.from_user.first_name} 😱😱!', parse_mode='markdown')

                            if message.from_user.id not in common.red_scour:
                                common.red_scour[message.from_user.id] = 1

                    except:
                        pass

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(option):
        query = option.data
        if query == 'join-jumble':
            join_game(query, option, 'mannual', common.sec60)

        elif query == 'next-jumble-word' and option.from_user.id not in common.scour_Dict.keys():
            alert(option.id, 'You are not a part of this game!')

        elif query == 'next-jumble-word' or query == '1next-jumble-word':
            if not (common.nextButtonCount):
                common.nextButtonCount = True  # for limiting the next button click
                common.time_breaker = True
                time.sleep(1)
                common.nextFlag = True
                join_game('join-jumble', option, 'mannual', 0)

    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
