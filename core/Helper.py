import json
import time

def get_message_stream(chatid):
	"""return message stream in json format with all information"""
    
	message_list = []
	with open(str(chatid)+".json", "r") as inFile:
		try:
			message_list = json.load(inFile)
		except ValueError:
			print("empty file")
	inFile.close()

	return message_list

def get_messages_of_user(chatid, user_id):
	"""return all messages from a certain user"""
	return [m for m in get_message_stream(chatid) if user_id == m['from_user']['id']]


def get_latest_messages(chatid, minutes):
	"""return all messages from the last time, specified in minutes"""
	message_list = get_message_stream(chatid)
	last_time = time.time() - minutes * 60 # unix time now
	return [m for m in message_list if m['date'] >= last_time]

def get_users_latest_messages(chatid, user_id):
	"""return all messages from a certain user to the first message of another user"""

	message_list = get_message_stream(chatid)
	users_messages = []

	for m in message_list:
		if m['from_user']['id'] == user_id:
			users_messages.append(m)
		else:
			return users_messages

	return users_messages

def one_text_from_meassage_stream(message_stream):
	message_text = ""
	for m in message_stream:
		message_text += m['text']

	return message_text

