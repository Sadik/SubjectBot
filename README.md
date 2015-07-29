# SubjectBot

This Bot is reading the chat messages and recognizes the subject people were talking about.
Note: The Bot needs to have access to messages.

Dependencies:
    pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI)
    pip install pyTelegramBotAPI

Also:
You need a file 'config.ini' in the same directory as the main file
with the following content:

    [Telegram]
    token: 1223456789:abcdefghijklmnopqrstu

This way I don't need to exclude lines from commit and I can't accidently commit my token
Well I can if I didn't add the config.ini to gitignore.
