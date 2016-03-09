#!/usr/bin/python3
import json
import time, datetime
import os
import os.path
import pickle
from core import EventFrame

chat_running = True

def execute_commands(m):
    """returns the answerText to subjectBot, where the Bot will give the text as reply, unless answerText is None.
    i.e. answerText should remain None if it's not intended to give a reply"""
    global chat_running
    text = m.text
    answerText = None
    if (text.startswith("/start")):
        answerText = start_chat(m)
    if (text.startswith("/stop") and chat_running):
        answerText = stop_chat(m)
    if (text.startswith("/delete_chat") and chat_running):
        answerText = delete_chat(m)
    if (text.startswith("/print_json") and chat_running):
        answerText = print_json(m)
    if (text.startswith("/delete_json") and chat_running):
        answerText = delete_json(m)
    if (text.startswith("/print_stats" or text.startswith("/stats")) and chat_running):
        answerText = print_stats(m)
    if (text.startswith("/tags")):
        answerText = show_tags(m)
    if (text.startswith("/frames")):
        answerText = show_frames(m)
    
    return answerText

#create json file if not existent
def start_chat(m):
    # create file only if it doesn't exist
    if (not os.path.isfile(str(m.chat.id)+".json")):
        f = open(str(m.chat.id)+".json", 'x')
        f.close()

    if (not os.path.isfile(str(m.chat.id)+"_frames")):
        f = open(str(m.chat.id)+"_frames", 'wb')
        f.close()

    suggestions = None
    try:
        f = open(str(m.chat.id)+"_frames", 'rb')
        suggestions = pickle.loads(f.read())
    except FileNotFoundError:
        open(str(m.chat.id)+"_data", 'x')
        print ("file created: " + str(m.chat.id)+"_data")
    except EOFError:
        f = open(str(m.chat.id)+"_data", 'wb')
        pickle.dump(suggestions, f)
    except:
        print("unknown error in start_chat")
        raise

    global chat_running
    if (chat_running):
        return "Bot läuft bereits"
    else:
        chat_running = True
        return "Bot wurde gestartet"

def stop_chat(m):
    global chat_running
    chat_running = False
    return "Bot wurde pausiert"

def show_tags(m):
    return """
    A - Action
P - Place
TS - Time Specification
PC - Participant (Name)
C - Cost
NV - negative value
PV - positive Value"""

def show_frames(m):
#create file if not exist
    if (not os.path.isfile(str(m.chat.id)+"_frames")):
        f = open(str(m.chat.id)+"_frames", 'wb')
        f.close()

    frame_list = []
    f = open(str(m.chat.id)+"_frames", "r+b") #read and write binary mode

    while 1:
        try:
            frame_list.append (pickle.load(f))
            frame_list = sum(frame_list, [])
        except EOFError:
            break
        except UnicodeDecodeError:
            print("UnicodeDecodeError!")
            print ("[WARNING]")
            print (EventFrame.EventFrame.readable_frame_list(frame_list))
            print ("[END OF WARNING]")
            return ("Warnung: Die Operation war nicht erfolgreich.")
        except:
            print("unknown error in start_chat")
            raise

    f.close()

    if len(frame_list) <= 0:
        return "Kein Vorschlag vorhanden"
    elif len(frame_list) == 1:
        return "1 Vorschlag gefunden.\n\n{0}".format(EventFrame.EventFrame.readable_frame_list(frame_list))
    else:
        return "{0} Vorschläge gefunden.\n\n{1}".format(len(frame_list), EventFrame.EventFrame.readable_frame_list(frame_list))

def delete_chat(m):
    chat_running = False
    f = open(str(m.chat.id)+".json", 'w+')
    f.close()
    return "Bot wurde gestoppt und chatlog gelöscht"

def string_splitter(line, chars_in_each_line):
    return [line[i:i + chars_in_each_line] for i in range(0, len(line), chars_in_each_line)]

def jdefault(m):
    return m.__dict__

def print_json(m):
    message_list = []
    with open(str(m.chat.id)+".json", "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            print("empty file")
            tb.send_message(m.chat.id,"Keine Nachrichten gefunden")
            return
    inFile.close()
    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    splits = string_splitter(json_string,2000)
    for s in splits:
        return s

def delete_json(m):
    open(str(m.chat.id)+".json", "w").close()
    return "chat log gelöscht."

def unixtime_to_readable_string(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime('%d.%m.%y, %H:%M Uhr')

def print_stats(m):
    message_list = []
    with open(str(m.chat.id)+".json", "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            print("empty file")
            return "Keine Nachrichten gefunden"
    inFile.close()

    user_message_counter = dict() # will hold {user_id: message count}
    user_dict = dict() # will hold {}
    oldest_time = time.time() # unix time now

    for message in message_list:
        user_id = message['from_user']['id']
        user_dict[user_id] = message['from_user']
        if (user_id in user_message_counter):
            user_message_counter[user_id] += 1
        else:
            user_message_counter[user_id] = 1
        #print ("user_message_count:" + str(user_message_counter))
        if (message['date'] < oldest_time):
            oldest_time = message['date']

    time_str = unixtime_to_readable_string(oldest_time)
    return "%d Nachrichten seit dem %s" % (len(message_list),time_str)

   # user_message_counter_string = ""
   # for key in user_message_counter:
   #     first_name = user_dict[key]['first_name']
   #     last_name = user_dict[key]['last_name']
   #     count = user_message_counter[key]
   #     user_message_counter_string += "%s %s: %s\n" % (first_name, last_name, count)
   # tb.send_message(m.chat.id, user_message_counter_string)
