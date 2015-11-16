# SubjectBot

This Bot is reading the chat messages and analyzes the text for specific infrmation (NER).
Note: The Bot needs to have access to messages.

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
