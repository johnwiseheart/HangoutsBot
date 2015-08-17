import hangups
import re

import random
import plugins


def _initialise(bot):
    plugins.register_user_command(["acrostic"])


def acrostic(bot, event, *args):
    words = open('/usr/share/dict/words').read().strip().split()
    for arg in args:
        letters = [letter.lower() for letter in arg]
        random_words = []
        for index, letter in enumerate(letters):
            if index == len(arg)-1:
                random_words.append(random.choice([word for word in words if word[0].lower() == letter and word[len(word)-2] != "'"]))
            else:
                random_words.append(random.choice([word for word in words if word[0].lower() == letter]))
        random_words = "<br />".join([word[0].upper() + word[1:] for word in random_words])
        msg = "".join([letter.upper() for letter in letters]) + ":<br /><br />" + random_words
        bot.send_html_to_conversation(event.conv_id, msg)

