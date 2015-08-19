#!/usr/bin/python3
import configparser
import telebot
from telebot import types
import time
import json

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Telegram']['token']
messagesDataFile = "messagesData"

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
    with open(messagesDataFile, "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            meessage_list = []
    inFile.close()
    message_list.append(m)
    print("message_list: " + str(message_list))
    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    #print ("json_string: " + json_string)
    #print (type(json_string))
    with open(messagesDataFile, "w") as outFile:
        outFile.write(json_string)
    outFile.close()

def print_json(m):
    message_list = []
    with open(messagesDataFile, "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            print("empty file")
            return
    inFile.close()
    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    splits = string_splitter(json_string,2000)
    for s in splits:
        tb.send_message(m.chat.id, s)

def delete_json(m):
    open(messagesDataFile, "w").close()

def execute_commands(m):
    text = m.text
    if (text.startswith("/print_json")):
        print_json(m)
    if (text.startswith("/delete_json")):
        delete_json(m)
    if (text.startswith("print_stats")):
        pass

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            collect_message(m)
            execute_commands(m)
            print_message_stats(m)
            tb.reply_to(m, "I am replying to your message")
        else:
            tb.reply_to(m, "Only text messages are supported")

def greetings(chatid):
    tb.send_message(chatid, "Ich wurde gestartet")

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
