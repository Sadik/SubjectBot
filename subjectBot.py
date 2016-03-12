#!/usr/bin/python3
import configparser
import telebot
from telebot import types
import json
import os.path
import subprocess
from core import BotCommands, MessageFilter, Helper

config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['Telegram']['token']

def print_message_stats(m):
    print ("###################################")
    print("MessageID:     %s" % m.message_id)
    print("ChatID         %s" % m.chat.id)
    print("UserID         %s" % (m.from_user.id))
    print("From:          %s %s (%s)" % (m.from_user.first_name
    , m.from_user.last_name, m.from_user.username))
    print("Date (unix):   " + str(m.date))
    print("Text:          %s" % m.text)

def jdefault(m):
    return m.__dict__

def collect_message(m):
    message_list = []
    try:
        if (not os.path.isfile(str(m.chat.id)+".json")):
            f = open(str(m.chat.id)+".json", 'w+')
            f.close()
        chatfile = open(str(m.chat.id)+".json", "r")
        try:
            message_list = json.load(chatfile)
        except FileNotFoundError:
            if (not os.path.isfile(str(m.chat.id)+".json")):
                f = open(str(m.chat.id)+".json", 'w+')
                f.close()
        except ValueError:
            print ("ValueError occurred in 'collect_message' method")
            meessage_list = []
        except IOError:
            if (not os.path.isfile(str(m.chat.id)+".json")):
                f = open(str(m.chat.id)+".json", 'w+')
                f.close()
        finally:
            chatfile.close()
    except NameError:
        print ("NameError occurred in 'collect_message' method")
        if (not os.path.isfile(str(m.chat.id)+".json")):
            f = open(str(m.chat.id)+".json", 'w+')
            f.close()

    message_list.append(m)
    json_string = json.dumps(message_list, default=jdefault, indent=4, sort_keys = True, ensure_ascii=False)
    with open(str(m.chat.id)+".json", "w") as outFile:
        outFile.write(json_string)
    outFile.close()

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    answerText = None
    for m in messages:
        print("received message from " + str(m.chat.id))
        chatid = m.chat.id
        if m.content_type == 'text':
            answerText = BotCommands.execute_commands(m)
            collect_message(m)
            print_message_stats(m)
        else:
            tb.reply_to(m, "Only text messages are supported")
            return

    if answerText is not None: #command was executed, send reply
        tb.send_message(m.chat.id, answerText)
    else:
        # start Filtering message for content
        mFilter = MessageFilter.MessageFilter(m)
        mFilter.NER()

        relevance = mFilter.isProbablyRelevant()
        if (relevance == 2):
            #tb.send_message(m.chat.id, "Deine Nachricht ist wahrscheinlich relevant.")
            print ("Deine Nachricht ist wahrscheinlich relevant.")
            #tb.send_message(m.chat.id, mFilter.showFlags())
            result = mFilter.updateOrCreateEventFrame(m)
            tb.send_message(m.chat.id, result)
        elif (relevance == 1):
            if (mFilter.isContextRelevant()):
                #tb.send_message(m.chat.id, "Deine Nachricht ist im Kontext relevant.")
                print ("Deine Nachricht ist im Kontext relevant.")
                tb.send_message(m.chat.id, mFilter.showFlags())
                result = mFilter.updateOrCreateEventFrame(m)
                tb.send_message(m.chat.id, result)
        else:
            #tb.send_message(m.chat.id, "irrelevant")
            print ("irrelevant")

        #users_messages = Helper.get_users_latest_messages(m.chat.id, m.from_user.id)
        #print ("users messages: " + str(len(users_messages)))
        #print (users_messages)


def greetings(chatid):
    tb.send_message(chatid, "Ich wurde gestartet")
    if (os.path.isfile("int-ip")):
        ipadress = subprocess.check_output(['./int-ip'])
        print ("Ich laufe unter folgender IP: {}".format(ipadress))
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
