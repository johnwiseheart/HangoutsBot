#!/usr/local/bin/python3
import sys, random
from bs4 import BeautifulSoup
import requests

import plugins

URL = 'http://pungenerator.org/puns?q={}&whole_words=0'

def _initialise(bot):
    plugins.register_user_command(["pun"])


def pun(bot, event, word, *args):
    r = requests.get(URL.format(word))

    soup = BeautifulSoup(r.text, 'html5lib')

    table = soup.find_all('table')[0]

    puns = [row.td.text.strip() for row in table.find_all('tr')[1:]]

    bot.send_html_to_conversation(event.conv_id, random.choice(puns))
