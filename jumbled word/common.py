import random
import time
import jumble
import DB_class
from DB_class import DynamoDB_con

DB = DynamoDB_con()

main_Dict_var = {}

# data, l       = DB.get_words()
# one_user_def_values = {"words":[],"chat_id":None,"gameStarted":0,"joinFlag":True,"chat_type":None,"gameCounter":0,"game_creater":{},"participants":[],"nextButtonCount":False,"nextEditButton":None,"editJoinMsg":None,"last_Right_ans":"","nextFlag":False,"total_players":0,"time_breaker":False,"word":'',"runner":0,"gessWord":'',"scour_Dict":{},"red_scour":{},"wait60sec":60,"wait40sec":40,"guessTime":40,"todayDate":'',"sessionId":0,"sec60":60}
# words         = []
# for dic in data:
#     words.append(dic['word'])
# chat_id       = None
# gameStarted   = False  # to block creating new game if one is going on
# joinFlag      = True  # to block joining patrticipants after 60 seconds
# chat_type = None
# gameCounter   = 0  # count the how many word appearead in a particular game
# game_creater  = {}  # storing data of who initiated the game
# participants  = []  # storing data of joined participants in a particular game
# nextButtonCount = False  # decision for next word
# nextEditButton  = None  # storing current (Next Word) button data
# editJoinMsg     = None
# last_Right_ans  = ''  # storing name of user who guessed current word
# nextFlag        = False  # show or hide next button
# total_players   = 0  # counting total participants
# time_breaker    = False  # decision on breaking timer
# word            = ''
# runner          = 0
# gessWord        = ''
# scour_Dict      = {}
# red_scour       = {}
# wait60sec       = 0  # waiting time for particiants to join the game (60)
# wait40sec       = 40  # waiting time for particiants to join the game (60
# guessTime       = 40  # waiting time to guess the word
# todayDate       = ''
# sessionId = 0

# # variiiii
# sec60           = 60

DB = DB_class.DynamoDB_con()

def get_jumble():
    try:
        global word, gameCounter, runner, gessWord
        # words = ['furze', 'fuses', 'fusee', 'fused', 'fusel', 'fuser', 'fussy', 'gales', 'galls', 'gamba', 'gamer', 'gamin']
        word = random.choices(words)[0].upper()
        jumble = ' '.join(random.sample(word, len(word)))
        jumbled = ''
        random_number = random.randrange(1, len(word))
        jumbled += word[0]+' '
        for i in range(1, len(word)):
            if i == random_number and len(word) > 4:
                jumbled += word[i]+' '
            else:
                jumbled += '_ '
        gameCounter += 1
        runner = 1
        gessWord = word
        return f'🔤 {len(word)} letters: *{jumble}* \n 🤔 : *{" ".join(jumbled)}*'
    except Exception as e:
        jumble.ErrorHandler(e)
        print('error in get_jumble function :@@@@@@@@@@@@ ', e)

def start_timer(name, sec, game, message):
    try:
        global wait60sec, runner, word
        for i in range(sec, -1, -1):
            if time_breaker:
                break
            time.sleep(1)
            wait60sec = i
            print(sec, i, name, runner)
            if i == 30 or i == 15:
                if name == 'join-wait':
                    jumble.create_game('/jumbleword', message, i)
                    runner == 2
            elif i == 0:
                word = ''
                if name == 'guess-wait' and runner == 1:
                    jumble.auto_next_word(message)
                    runner == 2
                elif name == 'join-wait':
                    jumble.join_game(game, message, 'auto', i)
                    runner == 2
                elif name == 'ques-wait' and runner == 3:  # after 40 sec of 1 word
                    jumble.winner(message, False)
                elif name == 'ques-wait' and runner == 0:
                    jumble.winner(message, False)
                break
    except Exception as e:
        print('error in start_timer function @@@@@@@@@@@@@@', e)
        jumble.ErrorHandler(e)