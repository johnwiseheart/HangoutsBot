import hangups

import random
import plugins


def _initialise(bot):
    plugins.register_user_command(["kill"])


def kill(bot, event, target, *args):

    verbs = ['shreks',
             'wobs up',
             'murders',
             'kills',
             'decimates',
             'stabs',
             'annihilates',
             'wrecks',
             'destroys',
             'spooks']
    weapons = ['a katana',
               'a dome',
               'some ants',
               'a donkey',
               'an intervention 50 cal rifle',
               'some weed',
               'an Arduino board',
               'a diamond sword',
               'gravity',
               'Java 1.8',
               'the Strategy Pattern']
    m = "Wobcke %s %s with %s." % (random.choice(verbs), target, random.choice(weapons))
    bot.send_html_to_conversation(event.conv_id, m)
