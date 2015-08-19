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
message_list = []

def print_message_stats(m):
    print ("###################################")
    print("MessageID:     %s" % m.message_id)
    print("ChatID         %s" % m.chat.id)
    print("UserID         %s" % (m.from_user.id))
    print("From:          %s %s" % (m.from_user.first_name
    , m.from_user.last_name))
    print("Date (unix):   " + str(m.date))
    print("Text:          %s" % m.text)

def collect_stats_from_message(m):
    message_id = m.message_id
    from_user = m.from_user
    chat_id = m.chat
    unixdate = m.date
    text = m.text

def jdefault(m):
    return m.__dict__

def collect_message(m):
    global message_list
    print ("collecting message")
    print(json.dumps(m, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False))
    #with open(messagesDataFile, "w") as outfile:
#        json.dump(m, outfile, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)


    with open(messagesDataFile, "r") as inFile:
        try:
            message_list = json.load(inFile)
        except ValueError:
            meessage_list = []

    message_list.append(m)
    print("message_list: " + str(message_list))

    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    print ("json_string: " + json_string)
    print (type(json_string))

    with open(messagesDataFile, "w") as outFile:
        outFile.write(json_string)

def execute_commands(m):
    text = m.text
    if (text.startswith("/stats")):
        tb.send_message(m.chat.id, "Updating stats")
        with open(messagesDataFile, "w") as outfile:
            json.dump(m, outfile, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            text = m.text
            execute_commands(m)
            tb.reply_to(m, "I am replying to you message")
            print_message_stats(m)
            collect_message(m)
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
