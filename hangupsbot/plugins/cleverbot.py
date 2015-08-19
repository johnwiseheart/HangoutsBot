import asyncio, hashlib, urllib

import urllib.request as urllib2
from http.cookiejar import CookieJar

from random import randrange, randint, random
import re
import hangups

import plugins


__cleverbots = dict()

""" Cleverbot API adapted from https://github.com/folz/cleverbot.py """
class Cleverbot:
    """
    Wrapper over the Cleverbot API.
    """
    HOST = "www.cleverbot.com"
    PROTOCOL = "http://"
    RESOURCE = "/webservicemin"
    API_URL = PROTOCOL + HOST + RESOURCE

    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept-Language': 'en-us,en;q=0.8,en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        'Host': HOST,
        'Referer': PROTOCOL + HOST + '/',
        'Pragma': 'no-cache'
    }

    def __init__(self):
        """ The data that will get passed to Cleverbot's web API """
        self.data = {
            'stimulus': '',
            'start': 'y',  # Never modified
            'sessionid': '',
            'vText8': '',
            'vText7': '',
            'vText6': '',
            'vText5': '',
            'vText4': '',
            'vText3': '',
            'vText2': '',
            'icognoid': 'wsf',  # Never modified
            'icognocheck': '',
            'fno': 0,  # Never modified
            'prevref': '',
            'emotionaloutput': '',  # Never modified
            'emotionalhistory': '',  # Never modified
            'asbotname': '',  # Never modified
            'ttsvoice': '',  # Never modified
            'typing': '',  # Never modified
            'lineref': '',
            'sub': 'Say',  # Never modified
            'islearning': 1,  # Never modified
            'cleanslate': False,  # Never modified
        }

        # the log of our conversation with Cleverbot
        self.conversation = []
        self.resp = str()

        # install an opener with support for cookies
        cookies = CookieJar()
        handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
        ]
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)

        # get the main page to get a cookie (see bug  #13)
        try:
            urllib2.urlopen(Cleverbot.PROTOCOL + Cleverbot.HOST)
        except urllib2.HTTPError:
            # TODO errors shouldn't pass unnoticed,
            # here and in other places as well
            return str()


    def ask(self, question):
        """Asks Cleverbot a question.

        Maintains message history.

        Args:
            q (str): The question to ask
        Returns:
            Cleverbot's answer
        """
        # Set the current question
        self.data['stimulus'] = question

        # Connect to Cleverbot's API and remember the response
        try:
            self.resp = self._send()
        except urllib2.HTTPError:
            # request failed. returning empty string
            return str()

        # Add the current question to the conversation log
        self.conversation.append(question)

        parsed = self._parse()

        # Set data as appropriate
        if self.data['sessionid'] != '':
            self.data['sessionid'] = parsed['conversation_id']

        answer = re.sub(r'\|([0-9A-F]{4})', fix_unicode, parsed['answer'])

        # Add Cleverbot's reply to the conversation log
        self.conversation.append(answer)

        return answer


    def _send(self):
        """POST the user's question and all required information to the
        Cleverbot API
        Cleverbot tries to prevent unauthorized access to its API by
        obfuscating how it generates the 'icognocheck' token, so we have
        to URLencode the data twice: once to generate the token, and
        twice to add the token to the data we're sending to Cleverbot.
        """
        # Set data as appropriate
        if self.conversation:
            linecount = 1
            for line in reversed(self.conversation):
                linecount += 1
                self.data['vText' + str(linecount)] = line
                if linecount == 8:
                    break

        # Generate the token
        enc_data = urllib.parse.urlencode(self.data)
        digest_txt = enc_data[9:35]
        token = hashlib.md5(digest_txt.encode('utf-8')).hexdigest()
        self.data['icognocheck'] = token

        # Add the token to the data
        enc_data = urllib.parse.urlencode(self.data).encode('utf-8')
        req = urllib2.Request(self.API_URL, enc_data, self.headers)

        # POST the data to Cleverbot's API
        conn = urllib2.urlopen(req)
        resp = conn.read()

        # Return Cleverbot's response
        return resp

    def _parse(self):
        """Parses Cleverbot's response"""
        parsed = [
            item.split('\r') for item in self.resp.decode('utf-8').split('\r\r\r\r\r\r')[:-1]
        ]
        parsed_dict = {
            'answer': parsed[0][0],
            'conversation_id': parsed[0][1],
            'conversation_log_id': parsed[0][2],
        }
        try:
            parsed_dict['unknown'] = parsed[1][-1]
        except IndexError:
            parsed_dict['unknown'] = None
        return parsed_dict


def _initialise(bot):
    plugins.register_handler(_handle_incoming_message, type="message")
    plugins.register_user_command(["chat"])
    plugins.register_handler(_scan_for_triggers)


@asyncio.coroutine
def _handle_incoming_message(bot, event, context):
    """Handle random message intercepting"""

    if not bot.get_config_suboption(event.conv_id, 'cleverbot_percentage_replies'):
        return

    percentage = bot.get_config_suboption(event.conv_id, 'cleverbot_percentage_replies')

    if randrange(0, 101, 1) < float(percentage):
        chat(bot, event, event.text)


def chat(bot, event, *args):
    """chat to Cleverbot"""
    if event.conv.id_ not in __cleverbots:
        __cleverbots[event.conv.id_] = Cleverbot()

    loop = asyncio.get_event_loop()
    text = yield from loop.run_in_executor(None, __cleverbots[event.conv.id_].ask, ' '.join(args))

    ad_text = ["Cleverscript.com.", "Clevermessage", "Clevertweet", "CleverEnglish"]
    for ad in ad_text:
        if ad.lower() in text.lower():
            return

    yield from bot.coro_send_message(event.conv.id_, text)

def _scan_for_triggers(bot, event, command):
    # chat one in one hundred times
    if random() < 0.01:
        chat(bot, event, event.text)


def fix_unicode(match):
    if match.group(1) is not None:
        return chr(int(match.group(1), 16))

