import sys, time
import json
import requests, markovgen

import plugins

def _initialise(bot):
    plugins.register_user_command(["sim", "simc", "simu", "simuc"])

def sim(bot, event, subreddit, *args):
    generate(bot, event, False, False, subreddit)
def simc(bot, event, subreddit, *args):
    generate(bot, event, True, False, subreddit)
def simu(bot, event, user, *args):
    generate(bot, event, False, True, user)
def simuc(bot, event, user, *args):
    generate(bot, event, True, True, user)

def generate(bot, event, comments, user, name):
    model = markovgen.Markov()
    for sentence in get_strings(name, limit=100, comments=comments, user=user):
        model.feed(sentence)
        sentences.append(sentence)

    bot.sent_html_to_conversation(event.conv_id, model.generate_markov_text())


    def get_strings(path, limit=1000, batch_size=100, comments=False, user=False):
        """Fetch a reddit listing from reddit.com."""

        session = requests.Session()
        session.headers.update({
            "User-Agent": "python:subreddit-sim-commandline:1.0 (by /u/ravrahn)",
        })

        if user:
            path = '/user/{}'.format(path)
        else:
            path = '/r/{}'.format(path)

        base_url = "https://api.reddit.com" + path

        if comments:
            base_url += "/comments"
        elif user:
            base_url += '/submitted'

        after = None
        count = 0
        while count < limit:
            params = {"limit": batch_size, "count": count}
            if after:
                params["after"] = after

            response = session.get(base_url, params=params)
            response.raise_for_status()

            listing = json.loads(response.text)["data"]

            for child in listing["children"]:
                if comments:
                    yield child["data"]["body"]
                else:
                    yield child["data"]["title"]
                count += 1

            after = listing["after"]
            if not after:
                break

            # obey reddit.com's ratelimits
            # see: https://github.com/reddit/reddit/wiki/API#rules
            if limit > batch_size:
                time.sleep(2)
