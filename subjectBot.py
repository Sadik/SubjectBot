#!/usr/bin/python3
import configparser
import telebot
from telebot import types
import time, datetime
import json
import os.path
import subprocess

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Telegram']['token']

chat_running = True

#create json file if not existent
def start_chat(m):
    global chat_running
    if (chat_running):
        tb.send_message(m.chat.id, "Bot läuft bereits")
    else:
        chat_running = True
        tb.send_message(m.chat.id, "Bot wurde gestartet")

    # create file only if it doesn't exist
    if (not os.path.isfile(str(m.chat.id)+".json")):
        f = open(str(m.chat.id)+".json", 'w+')
        f.close()

def stop_chat(m):
    global chat_running
    chat_running = False
    tb.send_message(m.chat.id, "Bot wurde pausiert")

def delete_chat(m):
    tb.send_message(m.chat.id, "Bot wurde gestoppt und chatlog gelöscht")
    chat_running = False
    f = open(str(m.chat.id)+".json", 'w+')
    f.close()

def print_message_stats(m):
    print ("###################################")
    print("MessageID:     %s" % m.message_id)
    print("ChatID         %s" % m.chat.id)
    print("UserID         %s" % (m.from_user.id))
    print("From:          %s %s" % (m.from_user.first_name
    , m.from_user.last_name))
    print("Date (unix):   " + str(m.date))
    print("Text:          %s" % m.text)

def jdefault(m):
    return m.__dict__

def string_splitter(line, chars_in_each_line):
    return [line[i:i + chars_in_each_line] for i in range(0, len(line), chars_in_each_line)]

def collect_message(m):
    message_list = []
    with open(str(m.chat.id)+".json", "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            meessage_list = []
    inFile.close()
    message_list.append(m)
    #print("message_list: " + str(message_list))
    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    #print ("json_string: " + json_string)
    #print (type(json_string))
    with open(str(m.chat.id)+".json", "w") as outFile:
        outFile.write(json_string)
    outFile.close()

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
        tb.send_message(m.chat.id, s)

def delete_json(m):
    open(str(m.chat.id)+".json", "w").close()

def print_stats(m):
    message_list = []
    with open(str(m.chat.id)+".json", "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            print("empty file")
            tb.send_message(m.chat.id,"Keine Nachrichten gefunden")
            return
    inFile.close()

    user_message_counter = dict() # wil hold {user_id: message count}
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
    tb.send_message(m.chat.id, "%d Nachrichten seit dem %s" % (len(message_list),time_str))

    user_message_counter_string = ""
    for key in user_message_counter:
        first_name = user_dict[key]['first_name']
        last_name = user_dict[key]['last_name']
        count = user_message_counter[key]
        user_message_counter_string += "%s %s: %s\n" % (first_name, last_name, count)
    tb.send_message(m.chat.id, user_message_counter_string)

def unixtime_to_readable_string(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime('%d.%m.%y, %H:%M Uhr')

def execute_commands(m):
    global chat_running
    text = m.text
    if (text.startswith("/start")):
        start_chat(m)
    if (text.startswith("/stop") and chat_running):
        stop_chat(m)
    if (text.startswith("/delete_chat") and chat_running):
        delete_chat(m)
    if (text.startswith("/print_json") and chat_running):
        print_json(m)
    if (text.startswith("/delete_json") and chat_running):
        delete_json(m)
    if (text.startswith("/print_stats" or text.startswith("/stats")) and chat_running):
        print_stats(m)

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            execute_commands(m)
            collect_message(m)
            print_message_stats(m)
        else:
            tb.reply_to(m, "Only text messages are supported")

def greetings(chatid):
    tb.send_message(chatid, "Ich wurde gestartet")
    if (os.path.isfile("int-ip")):
        ipadress = subprocess.check_output(['./int-ip'])
        tb.send_message(chatid, "Ich laufe unter folgender IP: {}".format(ipadress))

tb = telebot.TeleBot(TOKEN)
tb.set_update_listener(listener) #register listener
tb.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
tb.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
#tb.polling(interval=1)

greetings("43871286")
while True: # Don't let the main Thread end.
    pass

#commands for BotFather:
#start - startet den Bot
#stop - stoppt den Bot
#delete_chat - stoppt den Bot und löscht die chatlog
#print_json - zeigt die komplette json-Datei
#delete_json - löscht die komplette json-Datei
#print_stats - zeigt allgemeine Statistik
