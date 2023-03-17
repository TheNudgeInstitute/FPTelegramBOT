import threading
import os
import time
import telebot
from datetime import date
from datetime import datetime
import random
from telegram import InputFile
from dbcongif import DynamoDB_con


import common
game_time = datetime.now()
from dotenv import load_dotenv
load_dotenv() 
DB = DynamoDB_con()
participants = []
number_to_word = {1: "first word 1️⃣", 2: "second word 2️⃣", 3: "third word 3️⃣",4:"fourth word 4️⃣"}
print("Hi, Jumble here!", os.getenv('bot_username'))
bot = telebot.TeleBot(os.getenv('API_KEY'))
def restart():
    common.gameStarted   = False  
    common.joinFlag  = True     
    common.game_creater  = {}  
    common.total_players   = 0  
    common.participants  = []    
    common.editJoinMsg     = None 
    common.sec60 = 60 
    common.scour_Dict = {}    
    common.gameCounter   = 0  
    common.gameround = 0 
    common.scour_Dict = {}
    common.rotate_per_participants = 0 
    common.currentWord = ''
    common.currentrightWord = ''
    common.currentParticipantIndex = ''
    common.message_game = ""
    stop_threads = False

def genrate_sessionId():
    sessionData, totalSess = DB.read_read(os.environ.get('Temp_JumbledWord_Session', 'TB_Temp_JumbledWord_Session'))
    f = True

    def generateFun():
        common.sessionId = random.randrange(1000, 9999)
        for dic in sessionData:
            # print('dic: ', dic)
            if common.sessionId == dic['sessionId']:
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
    print(common.scour_Dict)
    for d in common.scour_Dict:
        data = {"ID": str(datetime.today() .timestamp()).replace('.', ''), "Datetime": str(datetime.now()), "User_Id": str(d), "Points_Scored": str(common.scour_Dict[d]['points']), "sessionId": common.scour_Dict[d]['sessionId']}
        print(data,'<<<<<<<<<<<<<<<<<<<<<<<<<')
        table_name = os.getenv('Temp_JumbledWord_Session')
        DB.send_data(data, table_name)
    points_list = []
    for key in common.scour_Dict:
        points_list.append(common.scour_Dict[key]['points'])
    if sum(points_list) >0:
        usernames = [common.scour_Dict[k]['user_name'] for k in common.scour_Dict]
        points = [common.scour_Dict[k]['points'] for k in common.scour_Dict]

        
        sorted_usernames = [x for _, x in sorted(zip(points, usernames), reverse=True)]
        sorted_points = sorted(points, reverse=True)  
        max_points = max(sorted_points)
        winner_name = [sorted_usernames[i] for i in range(len(sorted_points)) if sorted_points[i] == max_points]    
        output_string = "" 
        # winner_name = sorted_usernames[0]
        
        for i in range(len(sorted_usernames)): 
            output_string += f"{sorted_usernames[i]}: {sorted_points[i]}/{common.max_round+1} Questions Correct\n" 
        if len(winner_name)>1:
            winner_name = ",".join([winner_name[i] for i in range(len(winner_name))])
            bot.send_message(message.chat.id,f'Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉\n\n{output_string}\nCongratulations: {winner_name}\nYou both are the winner\n\nKeep it up and practice more..!!📚📚📚📚')
        else:
            winner_name = winner_name[0]
            bot.send_message(message.chat.id,f'Thank you for participating in the Jumble word Game! 🥳🎉🎉🎉\n\n{output_string}\nCongratulations: {winner_name}\nYou are the winner\n\nKeep it up and practice more..!!📚📚📚📚')
        sticker_file_id = 'CAACAgIAAxkBAAEH3o9j935Cvbup1Wr54tFO6awWbm2jiwACSQEAAladvQp1bSI3184pVC4E'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        restart()
    else:
        sticker_file_id = 'CAACAgIAAxkBAAEH4Zxj-JriMmWjh92vf6cdEupnknXOJgACAQEAAvcCyA--Bt0rrVjiJC4E'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        bot.send_message(message.chat.id,f'No one has a score greater than zero\n\nThank you for participating in the Jumble word Game! 🥳🎉🎉🎉\n\nKeep it up and practice more..!!📚📚📚📚')
        restart()
        

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
    common.editJoinMsg = bot.send_message(chat_id, f'Welcome To The Jumble Game.... \nYou Have  *⌛{t}* _s_ to Join',
            reply_markup=keyboard,
            parse_mode='markdown')
    if t == common.sec60:
        bot.send_message(
                chat_id, f'{first_name} joined. \nThere is now {common.total_players} players')
        bot.send_message(
                chat_id, f"Waiting For more players",
                parse_mode='markdown'
            )
        sticker_file_id = 'CAACAgIAAxkBAAEH4Vtj-ISjo8PAA7yTImhpawkdblKy8wAC_wAD9wLIDz7Q9EOOrMfoLgQ'
        bot.send_sticker(message.chat.id, sticker=sticker_file_id)
        common.scour_Dict[message.from_user.id] = {
                'points': 0, "user_name": message.from_user.first_name, "chat_id":message.chat.id,'sessionId': common.sessionId}
        print(common.scour_Dict)
        common.blockmsgwhilewaiting =True
        join_counter = threading.Thread(target=common.start_timer, args=('join-wait', t, 'join-jumble', common.editJoinMsg))
        try:
            join_counter.start()
        except:
            print("error in create game")

def join_game(message,t = 60):
    chat_id = message.json['message']['chat']['id']
    first_name = message.from_user.first_name
    if len(common.participants) <= 10 :
        common.total_players += 1
        common.participants.append(message.from_user.id)
        common.scour_Dict[message.from_user.id] = {
                    'points': 0, "user_name": message.from_user.first_name, "chat_id":chat_id, 'sessionId': common.sessionId}
        bot.send_message(
                            chat_id, f'{first_name} joined. \nThere are now {common.total_players} players')
        print(common.gameStarted,common.joinFlag,common.game_creater,common.total_players,common.scour_Dict,common.participants)
    else :
        bot.send_message(
                            chat_id, f'{first_name} You cannot join this game . Limit is reached . \n There are now {common.total_players} players')
        

def start_game(message):
    total_users_id = ""
    for i in common.participants:
        total_users_id+= str(i)+','
    data = {"Date":str(date.today()),"Datetime": str(datetime.now()), 'JumbledWord_InitiatedByUser_ID': str(common.participants[0]), "JumbledWord_Participation": len(common.participants),"participants_ids":total_users_id}
    table_name = os.getenv('JumbledWord_Engagement')
    DB.send_data(data, table_name)
    common.blockmsgwhilewaiting =False
    if len(common.participants) > 0:
        common.currentParticipantIndex = 0
        sendWord(message)
    else:
        print('Less')   

def sendWord(message):
    
    # print(common.gameround, common.max_round, common.currentParticipantIndex,len(common.participants))
    if common.currentParticipantIndex == len(common.participants):
        if common.gameround  < common.max_round:
            common.gameround += 1
            common.currentParticipantIndex = 0
            common.round_msg = True
        else:
            return winner(message)
    
    if common.round_msg:
        bot.send_message(message.chat.id,f'ROUND {common.gameround+1}')   
        common.round_msg = False
    print(common.gameround, common.max_round, common.currentParticipantIndex,len(common.participants))
    common.currentWord = common.get_jumble()
    print(common.currentrightWord)
    # print(common.participants,common.currentParticipantIndex)
    user = common.scour_Dict[common.participants[common.currentParticipantIndex]]
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
            telebot.types.InlineKeyboardButton(text='Pass', callback_data='Pass', activeforeground="Black", activebackground="red", pady=10),)                
    bot.send_message(
        message.chat.id, f'{user["user_name"]} \nHere is the {number_to_word[common.gameround+1]}\n {common.currentWord}\n',
        reply_markup=keyboard,
        parse_mode='markdown'
    )   
    
    first_name = message.from_user.first_name
    common.message_game = message
    common.stop_threads = False
    t1 = threading.Thread(target = common.run, args =(lambda : common.stop_threads, common.participants[common.currentParticipantIndex],15))
    t1.start()

def checkAnswer(message,mode = "auto"):
    print(mode)
    if mode == "auto":
        if message.from_user.id in common.participants:
            if common.participants[common.currentParticipantIndex] == message.from_user.id:
                # if common.currentrightWord == (message.text).upper():
                print(common.currentrightWord)
                print(common.hint_match_word)
                if (message.text).upper() in common.hint_match_word or common.currentrightWord == (message.text).upper() :
                    
                    common.stop_threads = True
                    bot.send_message(message.chat.id, f'Hurray🎊🥳🎉🎊🥳🎉\nYour answer is correct {message.from_user.first_name} ...')
                    common.scour_Dict[message.from_user.id]['points']  += 1
                    common.currentParticipantIndex += 1
                    sendWord(message)   
                else:
                    pass
            else:
                bot.send_message(message.chat.id, f"⛔It's not your turn. ⌛wait... {message.from_user.first_name} ...")
        else:
            bot.send_message(message.chat.id, f"Dear {message.from_user.first_name},\n You are not a part of the current game. wait until it gets it over.")
    elif mode == "time" :
        common.stop_threads = True
        bot.send_message(common.message_game.chat.id, f'⌛Time is up..\n Right answer is ....{common.currentrightWord}')
        common.currentParticipantIndex += 1
        sendWord(common.message_game)
        

    else:
        common.stop_threads = True
        bot.send_message(common.message_game.chat.id, f'You have pass the word🥺\n Right answer is ....{common.currentrightWord}')
        common.currentParticipantIndex += 1
        sendWord(common.message_game)
        
    
def main():
    
    @bot.message_handler(commands=['jumbleword'])
    def send_welcome(message):
        command = message.text
        genrate_sessionId()
        print(message.chat.type, '-> chat type', command)
        if command.startswith('/jumbleword') and not common.gameStarted:
            common.gameStarted = True
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
                # print(common.gameStarted,common.joinFlag,common.game_creater,common.total_players)
                create_game(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(message):
        query = message.data
        if query == 'join-jumble':
            if common.gameStarted:
                if message.from_user.id not in common.participants:
                    join_game(message,common.sec60)  
                else:
                    pass
            else:
                print(message)
                bot.send_message(message.json['message']['chat']['id'],f"Previous game was ended \n If you want to play restart the game ")
        else:
            # time.sleep(1)
            print(common.participants[common.currentParticipantIndex])
            if common.participants[common.currentParticipantIndex] == message.from_user.id:
                checkAnswer(message,mode="manual")
            else:
                print("pass")
                pass
            # print(message.json['data'])


    @bot.message_handler(content_types=['text'])
    def send_welcome(message): 
        if not common.blockmsgwhilewaiting:
            
            if common.gameStarted:

                checkAnswer(message)
            else:
                pass
        else:
            pass

    bot.polling(none_stop=True)



if __name__ == "__main__":
    main()
