# SubjectBot

This Bot is reading the chat messages and analyzes the text for specific infrmation (NER). The bot is collecting information on appointments (what, where, when, participants).

**Note**: The Bot needs to have access to messages.

works with python 3

Install Dependencies:
    pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI)
    pip install -r pipdependencies

download nltk stuff:
    
    $ python
    >>>import nltk
    >>>nltk.download()
    then chose to download 'all'

Also:
You need a file 'config.ini' in the same directory as the main file
with the following content:

    [Telegram]
    token: 1223456789:abcdefghijklmnopqrstu

This way I don't need to exclude lines from commit and I can't accidently commit my token.
