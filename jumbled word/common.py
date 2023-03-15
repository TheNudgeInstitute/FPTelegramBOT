import jumble
import time
import random   
import json
import pandas as pd
from dbcongif import DynamoDB_con
import enchant
from itertools import permutations

with open('dictionary.json', 'r') as file:
    words_dictionary = json.load(file)

gameStarted   = False  # to block creating new game if one is going on
joinFlag  = True     # to block joining patrticipants after 60 seconds
blockmsgwhilewaiting = False
game_creater  = {}  # storing data of who initiated the game
total_players   = 0  # counting total participants
participants  = []  # storing data of joined participants in a particular game

editJoinMsg     = None # within 60sec jo string show krni hai

sec60 = 60 # waiting for 60s to joining the players
scour_Dict = {}    # players details like score
sessionId = 0
gameCounter   = 0  # count the how many word appearead in a particular game
gameround = 0 # how many round in one game
max_round = 2
rotate_per_participants = 0 #Game rotate per participantes
currentWord = ''
currentrightWord = ''
currentParticipantIndex = None
message_game = ""
stop_threads = False
round_msg = True   # user ko round ka message


DB = DynamoDB_con()
columns_names = {0:['four_level_word','four_level_flag'],1:['five_level_word','five_level_flag'],2:['six_level_word','six_level_flag']}


def check_valid_words(scramble_word):
    d = enchant.Dict("en_US")

    jumbled = scramble_word

    perms = [''.join(p) for p in permutations(jumbled)]

    global found_words 
    valid_words = []
    for perm in perms:
        if d.check(perm):
            valid_words.append(perm)
    found_words = []
    for word in valid_words:
        if word in words_dictionary.keys():
            found_words.append(word)

    print(f"valid_words:{found_words},all_found_word:{valid_words}")
    return found_words

def match_hint(jumbled,found_words):
    global hint_match_word
    hint_match_word = []
    for word in found_words:
        if len(word) == len(jumbled):
           
            for i in range(len(word)):
                if jumbled[i] != "_" and jumbled[i] != word[i]:
                    break
            else:
                
                hint_match_word.append(word)

    print("Matching words:", hint_match_word)

def get_jumble():
    
    try:
        
        global currentrightWord
        
        # global word, gameCounter, runner, gessWord
        current_flag_name = columns_names[gameround]
        print(current_flag_name)
        result_dict = DB.get_words(current_flag_name[0],current_flag_name[1])
        print(result_dict)
        if len(result_dict) == 0:
            DB.update_all_values(current_flag_name[0],current_flag_name[1])
            result_dict = DB.get_words(current_flag_name[0],current_flag_name[1])
        
        words = result_dict[current_flag_name[0]]

        word = words.upper()
        print(word)
        def shuffle(word):
            jumble = ''.join(random.sample(word, len(word)))
            return jumble
        print(result_dict['word'])
        print(columns_names[gameround][1])
        DB.update_flag(result_dict['word'],columns_names[gameround][1])
        
        
        jumble = shuffle(word)
        
        while jumble == word:
            jumble = shuffle(word)
        print(jumble)
        check_valid_words(jumble)
        
        jumbled = ''
        random_number = random.randrange(0, len(word))
        print(len(word))
        for i in range(0, len(word)):
            if len(word) == 3:
                if i == 1:
                    jumbled += word[i]
                else:
                    jumbled+="_"
            elif len(word) == 6:
                if i == 1 or i ==4:
                    jumbled += word[i]
                else:
                    jumbled+="_"
                
            else:
                if i == random_number-1 or i ==random_number+2:
                    jumbled += word[i]
                else:
                    jumbled += '_'
        gessWord = word
        currentrightWord = word
        # print(jumbled)
        match_hint(jumbled,found_words)
        return f'🔤{len(word)} letters: *{jumble}* \n🤔 : *{" ".join(jumbled)}*'
    except Exception as e:
        print('error in get_jumble function :@@@@@@@@@@@@ ', e)


def start_timer(name, sec, game, message):
    try:
        for i in range(sec, -1, -1):
            time.sleep(1)
            print(sec, i, name)
            if i == 30 or i == 15:
                if name == "join-wait":
                    jumble.create_game( message, i)
                   
            elif i == 0:  
                if name == "join-wait":
                    # if len(participants)>1:
                    jumble.start_game(message)
                    # else:
                        
                    #     jumble.onlyoneplayer(message)
                elif name == "player-wait":
                    print(message)
                    jumble.checkAnswer(message,mode="manual")
                    break
    except Exception as e:
        print('error in start_timer function @@@@@@@@@@@@@@', e)



def run(stop,message,sec):
    for i in range(sec, -1, -1):
        time.sleep(1)
        print(sec, i)
        if i == 0:
            jumble.checkAnswer(message,mode="time")

            
        elif  stop():
            print("Theadring Killed")
            break
        