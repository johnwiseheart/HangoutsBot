#!/usr/local/bin/python

from __future__ import division

import sys
import collections
import html
import itertools
import random
import time
import string
import json

import requests
import plugins

def _initialise(bot):
    plugins.register_user_command(["sim", "simc", "simu", "simuc"])

def simu(bot, event, user, *args):
    subreddit_path = "/user/{}/submitted".format(user)

    subs = TextGenerator(order=8)
    for sub in get_strings(subreddit_path, limit=100, comments=False):
      subs.add_sample(html.unescape(sub))

    bot.send_html_to_conversation(event.conv_id, subs.generate())

def simuc(bot, event, user, *args):
    subreddit_path = "/user/{}".format(user)

    comments = TextGenerator(order=8)
    for comment in get_strings(subreddit_path, limit=100, comments=True):
        comments.add_sample(html.unescape(comment))

    bot.send_html_to_conversation(event.conv_id, comments.generate())


def sim(bot, event, subreddit, *args):
    subreddit_path = "/r/{}".format(subreddit)

    titles = TextGenerator(order=5)
    for link in get_strings(subreddit_path, limit=100, comments=False):
        titles.add_sample(html.unescape(link))

    bot.send_html_to_conversation(event.conv_id, titles.generate())

def simc(bot, event, subreddit, *args):
    subreddit_path = "/r/{}".format(subreddit)

    comments = TextGenerator(order=8)
    for comment in get_strings(subreddit_path, limit=100, comments=comments):
        comments.add_sample(html.unescape(comment))

    bot.send_html_to_conversation(event.conv_id, comments.generate())

def weighted_lottery(weights, _random=random.random):
    """Randomly choose a key from a dict where values are weights.
    Weights should be non-negative numbers, and at least one weight must be
    non-zero. The probability that a key will be selected is proportional to
    its weight relative to the sum of all weights. Keys with zero weight will
    be ignored.
    Raises ValueError if weights is empty or contains a negative weight.
    """

    total = sum(weights.values())
    if total <= 0:
        raise ValueError("total weight must be positive")

    r = _random() * total
    t = 0
    for key, weight in weights.items():
        if weight < 0:
            raise ValueError("weight for %r must be non-negative" % key)
        t += weight
        if t > r:
            return key

    # this point should never be reached
    raise ValueError(
        "weighted_lottery messed up: r=%r, t=%r, total=%r" % (r, t, total))

class TextGenerator(object):
    """A Markov Chain based text mimicker."""

    def __init__(self, order=8):
        self.order = order
        self.starts = collections.Counter()
        self.start_lengths = collections.defaultdict(collections.Counter)
        self.models = [
            collections.defaultdict(collections.Counter)
            for i in range(self.order)]

    @staticmethod
    def _in_groups(input_iterable, n):
        iterables = itertools.tee(input_iterable, n)
        for offset, iterable in enumerate(iterables):
            for _ in range(offset):
                next(iterable, None)
        return zip(*iterables)

    def add_sample(self, sample):
        """Add a sample to the model of text for this generator."""

        if len(sample) <= self.order:
            return

        start = sample[:self.order]
        self.starts[start] += 1
        self.start_lengths[start][len(sample)] += 1
        for order, model in enumerate(self.models, 1):
            for chars in self._in_groups(sample, order+1):
                prefix = "".join(chars[:-1])
                next_char = chars[-1]
                model[prefix][next_char] += 1

    def generate(self):
        """Generate a string similar to samples previously fed in."""

        start = weighted_lottery(self.starts)
        desired_length = weighted_lottery(self.start_lengths[start])
        desired_length = max(desired_length, self.order)

        generated = []
        generated.extend(start)
        while len(generated) < desired_length:
            # try each model, from highest order down, til we find
            # something
            for order, model in reversed(list(enumerate(self.models, 1))):
                current_prefix = "".join(generated[-order:])
                frequencies = model[current_prefix]
                if frequencies:
                    generated.append(weighted_lottery(frequencies))
                    break
            else:
                generated.append(random.choice(string.ascii_lowercase))

        return "".join(generated)

def get_strings(path, limit=1000, batch_size=100, comments=False):
    """Fetch a reddit listing from reddit.com."""

    session = requests.Session()
    session.headers.update({
        "User-Agent": "python:subreddit-sim-commandline:1.0 (by /u/ravrahn)",
    })

    base_url = "https://api.reddit.com" + path

    if comments:
        base_url += "/comments"

    after = None
    count = 0
    while count < limit:
        params = {"limit": batch_size, "count": count}
        if after:
            params["after"] = after
        print(base_url)
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
