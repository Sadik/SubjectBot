#!/usr/bin/python3
import configparser
import telebot
from telebot import types
import json
import os.path
import subprocess
from core import BotCommands

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Telegram']['token']


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

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    answerText = None
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            answerText = BotCommands.execute_commands(m)
            collect_message(m)
            print_message_stats(m)
        else:
            tb.reply_to(m, "Only text messages are supported")

    if answerText is not None:
        tb.send_message(m.chat.id, answerText)

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
