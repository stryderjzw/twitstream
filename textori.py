#!/usr/bin/env python

# With the deepest affection for the original:
# http://twistori.com/

import textwrap
import asyncore
import getpass
import re
import htmlentitydefs
from xml.sax import saxutils
try:
    import json as simplejson
except ImportError:
    import simplejson

import twitter
import twitstream

USAGE = """%prog [options] [[keyword1] keyword2 ...]

Pretty-prints status messages that match one of the keywords.

Inspired by http://twistori.com/"""


class Formatter(object):
    
    url_pat = re.compile(r'\b(http://\S+[^\s\.\,\?\)\]\>])', re.IGNORECASE)
    ent_pat = re.compile("&#?\w+;")
    
    def __init__(self, keywords=[]):
        self.kw_pat = re.compile('\\b(%s)\\b' % "|".join(keywords), re.IGNORECASE)
        self.wrap = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')
    
    def __call__(self, status):
        st = twitter.Status.NewFromJsonDict(status)
        print '\033[94m' + st.user.screen_name + ':\033[0m'
        mess = self.ent_pat.sub(self.unescape, st.text)
        mess = self.wrap.fill(mess)
        mess = self.kw_pat.sub(self.bold, mess)
        mess = self.url_pat.sub(self.underline, mess)
        print mess
     
    @staticmethod
    def bold(m):
        return '\033[1m' + m.group(1) + '\033[0m'
    
    @staticmethod    
    def underline(m):
        return '\033[4m' + m.group(1) + '\033[0m'
    
    @staticmethod
    def unescape(m):
        "http://effbot.org/zone/re-sub.htm#unescape-html"
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    

if __name__ == '__main__':
    twitstream.parser.usage = USAGE
    (options, args) = twitstream.parser.parse_args()
    
    if not options.username:
        twitstream.parser.error("Username required")
    if not options.password:
        options.password = getpass.getpass(prompt='Password for %s: ' % options.username)
    if len(args) < 1:
        args = ['love', 'hate', 'think', 'believe', 'feel', 'wish']
    
    prettyprint = Formatter(args)
    
    twitstream.track(options.username, options.password, prettyprint, args, options.debug)
    
    asyncore.loop()
