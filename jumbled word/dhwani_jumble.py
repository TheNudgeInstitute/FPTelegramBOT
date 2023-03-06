import threading
import os
import time
import telebot
from datetime import date
from datetime import datetime
import random
from telegram import InputFile
from dbcongif import DynamoDB_con


import dhwani_common
game_time = datetime.now()
from dotenv import load_dotenv
load_dotenv() 
DB = DynamoDB_con()
participants = []
number_to_word = {1: "first word 1️⃣", 2: "second word 2️⃣", 3: "third word 3️⃣",4:"fourth word 4️⃣"}
print("Hi, Jumble here!", os.getenv('bot_username'))
bot = telebot.TeleBot(os.getenv('API_KEY'))
def restart():
    dhwani_common.gameStarted   = False  
    dhwani_common.joinFlag  = True     
    dhwani_common.game_creater  = {}  
    dhwani_common.total_players   = 0  
    dhwani_common.participants  = []    
    dhwani_common.editJoinMsg     = None 
    dhwani_common.sec60 = 60 
    dhwani_common.scour_Dict = {}    
    dhwani_common.gameCounter   = 0  
    dhwani_common.gameround = 0 
    dhwani_common.scour_Dict = {}
    dhwani_common.rotate_per_participants = 0 
    dhwani_common.currentWord = ''
    dhwani_common.currentrightWord = ''
    dhwani_common.currentParticipantIndex = ''
    dhwani_common.message_game = ""
    stop_threads = False

def genrate_sessionId():
    sessionData, totalSess = DB.read_read(os.environ.get('Temp_JumbledWord_Session', 'TB_Temp_JumbledWord_Session'))
    f = True

    def generateFun():
        dhwani_common.sessionId = random.randrange(1000, 9999)
        for dic in sessionData:
            # print('dic: ', dic)
            if dhwani_common.sessionId == dic['sessionId']:
                f = False
                break
    while True:
        # print('while:True')
        generateFun()
        if f:
            break


def onlyoneplayer(message):
    
    bot.send_message(message.chat.id,"You need atleast 2 players to play this game !! \n \nHappy learning📚📚📚📚")
    sticker_file_id = 'CAACAgIAAxkBAAEH4bZj-KOxV25C4he-omIgISXgBrB9pgAC_QAD9wLIDwLd5i1t00fWLgQ'
    bot.send_sticker(message.chat.id, sticker=sticker_file_id)
    restart()
def winner(message):
    print(dhwani_common.scour_Dict)
    for d in dhwani_common.scour_Dict:
        data = {"ID": str(datetime.today() .timestamp()).replace('.', ''), "Datetime": str(datetime.now()), "User_Id": str(d), "Points_Scored": str(dhwani_common.scour_Dict[d]['points']), "sessionId": dhwani_common.scour_Dict[d]['sessionId']}
        print(data,'<<<<<<<<<<<<<<<<<<<<<<<<<')
        table_name = os.getenv('Temp_JumbledWord_Session')
        DB.send_data(data, table_name)
    points_list = []
    for key in dhwani_common.scour_Dict:
        points_list.append(dhwani_common.scour_Dict[key]['points'])
    if sum(points_list) >0:
        usernames = [dhwani_common.scour_Dict[k]['user_name'] for k in dhwani_common.scour_Dict]
        points = [dhwani_common.scour_Dict[k]['points'] for k in dhwani_common.scour_Dict]

        
        sorted_usernames = [x for _, x in sorted(zip(points, usernames), reverse=True)]
        sorted_points = sorted(points, reverse=True)  
            
        output_string = "" 
        winner_name = sorted_usernames[0]
        
        for i in range(len(sorted_usernames)): 
            output_string += f"{sorted_usernames[i]}: {sorted_points[i]}/4 Questions Correct\n" 
        bot.send_message(message.chat.id,f'Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉\n\n{output_string}\nCongratulations: {winner_name}\nYou are the winner\n\nKeep it up and practice more..!!📚📚📚📚')
        sticker_file_id = 'CAACAgIAAxkBAAEH3o9j935Cvbup1Wr54tFO6awWbm2jiwACSQEAAladvQp1bSI3184pVC4E'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        restart()
    else:
        sticker_file_id = 'CAACAgIAAxkBAAEH4Zxj-JriMmWjh92vf6cdEupnknXOJgACAQEAAvcCyA--Bt0rrVjiJC4E'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        bot.send_message(message.chat.id,f'No one has a score greater than zero\n\nThank you for participating in the Jumble word Game! 🥳🎉🎉🎉\n\nKeep it up and practice more..!!📚📚📚📚')
        

def create_game(message,t=60):
    keyboard = telebot.types.InlineKeyboardMarkup()
    chat_id = message.chat.id
    print('Type of game ............................./jumbleword'+os.getenv("bot_username"),)
    print('---------------------------------------> inside create game ')
    keyboard.row(
            telebot.types.InlineKeyboardButton(text='Join Game 🎮', callback_data='join-jumble', color= "blue",activeforeground="red", activebackground="pink", pady=10),)
    first_name = message.from_user.first_name
    if t == 60:
        sticker_file_id = 'CAACAgIAAxkBAAEH4M1j-FM8HDulfZPS2EKXrNzJeDfZlAACrwsAAv1pgUph8CTBF6FPxC4E'
        bot.send_sticker(chat_id, sticker=sticker_file_id)
    else:
        pass
    dhwani_common.editJoinMsg = bot.send_message(chat_id, f'Welcome To The Jumble Game.... \nYou Have  *⌛{t}* _s_ to Join',
            reply_markup=keyboard,
            parse_mode='markdown')
    if t == dhwani_common.sec60:
        bot.send_message(
                chat_id, f'{first_name} joined. \nThere is now {dhwani_common.total_players} players')
        bot.send_message(
                chat_id, f"Waiting For more players",
                parse_mode='markdown'
            )
        sticker_file_id = 'CAACAgIAAxkBAAEH4Vtj-ISjo8PAA7yTImhpawkdblKy8wAC_wAD9wLIDz7Q9EOOrMfoLgQ'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        dhwani_common.scour_Dict[message.from_user.id] = {
                'points': 0, "user_name": message.from_user.first_name, "chat_id":message.chat.id,'sessionId': dhwani_common.sessionId}
        print(dhwani_common.scour_Dict)
        dhwani_common.blockmsgwhilewaiting =True
        join_counter = threading.Thread(target=dhwani_common.start_timer, args=('join-wait', t, 'join-jumble', dhwani_common.editJoinMsg))
        try:
            join_counter.start()
        except:
            print("error in create game")

def join_game(message,t = 60):
    chat_id = message.json['message']['chat']['id']
    first_name = message.from_user.first_name
    if len(dhwani_common.participants) <= 10 :
        dhwani_common.total_players += 1
        dhwani_common.participants.append(message.from_user.id)
        dhwani_common.scour_Dict[message.from_user.id] = {
                    'points': 0, "user_name": message.from_user.first_name, "chat_id":chat_id, 'sessionId': dhwani_common.sessionId}
        bot.send_message(
                            chat_id, f'{first_name} joined. \nThere are now {dhwani_common.total_players} players')
        print(dhwani_common.gameStarted,dhwani_common.joinFlag,dhwani_common.game_creater,dhwani_common.total_players,dhwani_common.scour_Dict,dhwani_common.participants)
    else :
        bot.send_message(
                            chat_id, f'{first_name} You cannot join this game . Limit is reached . \n There are now {dhwani_common.total_players} players')
        

def start_game(message):
    total_users_id = ""
    for i in dhwani_common.participants:
        total_users_id+= str(i)+','
    data = {"Date":str(date.today()),"Datetime": str(datetime.now()), 'JumbledWord_InitiatedByUser_ID': str(dhwani_common.participants[0]), "JumbledWord_Participation": len(dhwani_common.participants),"participants_ids":total_users_id}
    table_name = os.getenv('JumbledWord_Engagement')
    DB.send_data(data, table_name)
    dhwani_common.blockmsgwhilewaiting =False
    if len(dhwani_common.participants) > 0:
        dhwani_common.currentParticipantIndex = 0
        sendWord(message)
    else:
        print('Less')   

def sendWord(message):
    
    # print(dhwani_common.gameround, dhwani_common.max_round, dhwani_common.currentParticipantIndex,len(dhwani_common.participants))
    if dhwani_common.currentParticipantIndex == len(dhwani_common.participants):
        if dhwani_common.gameround  < dhwani_common.max_round:
            dhwani_common.gameround += 1
            dhwani_common.currentParticipantIndex = 0
            dhwani_common.round_msg = True
        else:
            return winner(message)
    
    if dhwani_common.round_msg:
        bot.send_message(message.chat.id,f'ROUND {dhwani_common.gameround+1}')   
        dhwani_common.round_msg = False
    print(dhwani_common.gameround, dhwani_common.max_round, dhwani_common.currentParticipantIndex,len(dhwani_common.participants))
    dhwani_common.currentWord = dhwani_common.get_jumble()
    print(dhwani_common.currentrightWord)
    # print(dhwani_common.participants,dhwani_common.currentParticipantIndex)
    user = dhwani_common.scour_Dict[dhwani_common.participants[dhwani_common.currentParticipantIndex]]
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
            telebot.types.InlineKeyboardButton(text='Pass', callback_data='Pass', activeforeground="Black", activebackground="red", pady=10),)                
    bot.send_message(
        message.chat.id, f'{user["user_name"]} \nHere is the {number_to_word[dhwani_common.gameround+1]}\n {dhwani_common.currentWord}\n',
        reply_markup=keyboard,
        parse_mode='markdown'
    )
    
    first_name = message.from_user.first_name
    dhwani_common.message_game = message
    dhwani_common.stop_threads = False
    t1 = threading.Thread(target = dhwani_common.run, args =(lambda : dhwani_common.stop_threads, dhwani_common.participants[dhwani_common.currentParticipantIndex],15))
    t1.start()

def checkAnswer(message,mode = "auto"):
    print(mode)
    if mode == "auto":
        if message.from_user.id in dhwani_common.participants:
            if dhwani_common.participants[dhwani_common.currentParticipantIndex] == message.from_user.id:
                # if dhwani_common.currentrightWord == (message.text).upper():
                print(dhwani_common.currentrightWord)
                print(dhwani_common.hint_match_word)
                if (message.text).upper() in dhwani_common.hint_match_word or dhwani_common.currentrightWord == (message.text).upper() :
                    
                    dhwani_common.stop_threads = True
                    bot.send_message(message.chat.id, f'Hurray🎊🥳🎉🎊🥳🎉\nYour answer is correct {message.from_user.first_name} ...')
                    dhwani_common.scour_Dict[message.from_user.id]['points']  += 1
                    dhwani_common.currentParticipantIndex += 1
                    sendWord(message)   
                else:
                    pass
            else:
                bot.send_message(message.chat.id, f"⛔It's not your turn. ⌛wait... {message.from_user.first_name} ...")
        else:
            bot.send_message(message.chat.id, f"Dear {message.from_user.first_name},\n You are not a part of the current game. wait until it gets it over.")
    elif mode == "time" :
        dhwani_common.stop_threads = True
        bot.send_message(dhwani_common.message_game.chat.id, f'⌛Time is up..\n Right answer is ....{dhwani_common.currentrightWord}')
        dhwani_common.currentParticipantIndex += 1
        sendWord(dhwani_common.message_game)
        

    else:
        dhwani_common.stop_threads = True
        bot.send_message(dhwani_common.message_game.chat.id, f'You have pass the word🥺\n Right answer is ....{dhwani_common.currentrightWord}')
        dhwani_common.currentParticipantIndex += 1
        sendWord(dhwani_common.message_game)
        
    
def main():
    
    @bot.message_handler(commands=['jumbleword'])
    def send_welcome(message):
        command = message.text
        genrate_sessionId()
        print(message.chat.type, '-> chat type', command)
        if command.startswith('/jumbleword') and not dhwani_common.gameStarted:
            dhwani_common.gameStarted = True
            if dhwani_common.joinFlag:
                dhwani_common.total_players += 1
                dhwani_common.game_creater = {
                    "date": game_time,
                    "InitiatedBy": message.from_user.id,
                    "total_common.participants": 0
                }
                dhwani_common.participants.append(message.from_user.id)
                dhwani_common.joinFlag = False
                dhwani_common.gameStarted = True
                # print(dhwani_common.gameStarted,dhwani_common.joinFlag,dhwani_common.game_creater,dhwani_common.total_players)
                create_game(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(message):
        query = message.data
        if query == 'join-jumble':
            if dhwani_common.gameStarted:
                if message.from_user.id not in dhwani_common.participants:
                    join_game(message,dhwani_common.sec60)  
                else:
                    pass
            else:
                print(message)
                bot.send_message(message.json['message']['chat']['id'],f"Previous game was ended \n If you want to play restart the game ")
        else:
            # time.sleep(1)
            print(dhwani_common.participants[dhwani_common.currentParticipantIndex])
            if dhwani_common.participants[dhwani_common.currentParticipantIndex] == message.from_user.id:
                checkAnswer(message,mode="manual")
            else:
                print("pass")
                pass
            # print(message.json['data'])


    @bot.message_handler(content_types=['text'])
    def send_welcome(message): 
        if not dhwani_common.blockmsgwhilewaiting:
            
            if dhwani_common.gameStarted:

                checkAnswer(message)
            else:
                pass
        else:
            pass

    bot.polling(none_stop=True)



if __name__ == "__main__":
    main()