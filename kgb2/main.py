# coding: utf-8
'''
author: Gabriel Pettier, Matthew Einhorn
'''

import sys
import os
import hmac
import requests
from json import loads
from hashlib import sha1, sha256
from irc.bot import SingleServerIRCBot
from flask import Flask, request, abort
from threading import Thread
from collections import OrderedDict, defaultdict


SERVERS = [('irc.freenode.net', 6667)]
GITHUB_SECRET = os.environ.get('GITHUB_SECRET', '')
TRAVIS_TOKEN = os.environ.get('TRAVIS_TOKEN', '')
COLOR_REPO = 3
COLOR_BRANCH = 4
COLOR_ISSUE = 4
COLOR_USER = 3
COLOR_URL = 15
DEFAULT_COLOR = 6
PASS_COLOR = 9
FAIL_COLOR = 4

NICKNAME = 'KGB-007'

if not GITHUB_SECRET or not TRAVIS_TOKEN:
    print('No SECRET defined!')
    sys.exit(1)

short_url_cache = OrderedDict()
repo_status = defaultdict(str)


def color(n, msg, url=False):
    if url:
        return '\x03{0:>02} {1} \x0300'.format(n, msg)
    else:
        return '\x03{0:>02}{1}\x0300'.format(n, msg)


class KGB(SingleServerIRCBot):
    '''Main class, this is the bot that connect to irc and listen for commands
    '''

    chans = ['#kivy-dev']

    def check(self, name, repo, signal, content):
        return True

    def on_welcome(self, serv, event):
        ''' what to do when server is joined
        '''
        self.serv = serv
        for name in self.chans:
            serv.join(name)
        print('Joined server:', self.serv)

    def get_short_url(self, url):
        if url in short_url_cache:
            return short_url_cache[url]
        req = requests.post('https://git.io/create',
                data={'url': url})
        if req.status_code != 200:
            return url
        surl = 'https://git.io/' + req.text
        short_url_cache[url] = surl
        if len(short_url_cache) > 1000:
            short_url_cache.popitem(last=False)
        return surl

    def shorten(self, text):
        text = text.replace('\n', '').replace('\r', '')
        if len(text) < 40:
            return text
        return text[:40] + '...'

    def treat_signal_hub(self, event, content):
        target = ''
        issue = ''
        if event == 'commit_comment':
            url = content['comment']['html_url']
            user = content['sender']['login']
            body = content['comment']['body']
            repo = content['repository']['full_name']
            target = content['repository']['default_branch']
            action = 'commented'
        elif event == 'create':
            url = content['repository']['html_url']
            user = content['sender']['login']
            if content['ref_type'] != 'repository':
                body = content['ref']
            else:
                body = content['repository']['name']
            repo = content['repository']['full_name']
            action = 'created'
        elif event == 'delete':
            url = content['repository']['html_url']
            user = content['sender']['login']
            body = content['ref']
            repo = content['repository']['full_name']
            action = 'deleted'
        elif event == 'gollum':
            url = content['pages'][0]['html_url']
            user = content['sender']['login']
            if len(content['pages']) == 1:
                body = content['pages'][0]['page_name']
            else:
                body = '{} pages "{}"'.format(
                    len(content['pages']), content['pages'][0]['page_name'])
            repo = content['repository']['full_name']
            action = content['pages'][0]['action']
            target = 'wiki'
        elif event == 'issue_comment':
            url = content['comment']['html_url']
            user = content['sender']['login']
            body = content['comment']['body']
            repo = content['repository']['full_name']
            if content['action'] == 'created':
                action = 'commented'
            else:
                action = content['action'] + ' comment'
            issue = content['issue']['number']
        elif event == 'issues':
            if content['action'] not in ('opened', 'closed', 'reopened'):
                return
            url = content['issue']['html_url']
            user = content['sender']['login']
            body = content['issue']['title']
            repo = content['repository']['full_name']
            action = content['action']
            issue = content['issue']['number']
        elif event == 'pull_request':
            if content['action'] not in (
                    'opened', 'closed', 'reopened', 'synchronize'):
                return
            url = content['pull_request']['html_url']
            user = content['sender']['login']
            body = content['pull_request']['title']
            repo = content['repository']['full_name']
            action = content['action']
            if action == 'closed' and content['pull_request']['merged']:
                action = 'merged from ' + content['pull_request']['user']['login']
            if action == 'synchronize':
                action = 'updated'
            issue = content['pull_request']['number']
        elif event == 'pull_request_review_comment':
            url = content['comment']['html_url']
            user = content['sender']['login']
            body = content['comment']['body']
            repo = content['repository']['full_name']
            if content['action'] == 'created':
                action = 'commented'
            else:
                action = content['action'] + ' comment'
            issue = content['pull_request']['number']
        elif event == 'push':
            if not content['commits']:
                return
            author = content['commits'][0]['author']['username']
            for commit in content['commits']:
                if commit['author']['username'] != author:
                    break
                repo = content['repository']['full_name']
                if repo.startswith('kivy/'):
                    repo = repo[5:]
                repo = color(COLOR_REPO, '[{}]'.format(repo))
                user = color(COLOR_USER, commit['author']['username'])
                body = color(DEFAULT_COLOR, '* ' + self.shorten(commit['message']) + ' -')
                url = color(COLOR_URL, self.get_short_url(commit['url']))
                action = color(DEFAULT_COLOR, 'committed')
                target = color(DEFAULT_COLOR, content['ref'].split('/')[-1])

                res = '{} {} {} {} {} {}'.format(repo, target, user, action, body, url)
                self.publish_message(res)
            return
        elif event == 'release':
            user = content['release']['author']['login']
            url = content['release']['html_url']
            body = 'tag {} in {}'.format(
                content['release']['tag_name'],
                content['release']['target_commitish'])
            repo = content['repository']['full_name']
            if content['action'] == 'published':
                action = 'released'
            else:
                action = content['action'] + ' release'
        elif event == 'repository':
            user = content['sender']['login']
            url = content['repository']['html_url']
            body = content['repository']['description']
            repo = content['repository']['full_name']
            action = content['action']
        elif event in ('deployment', 'deployment_status', 'public'):
            print('Got possibly interesting event "{}"'.format(event))
            return
        elif event in ('download', 'follow', 'fork_apply', 'gist'):
            # print('Got outdated event "{}"'.format(event))
            return
        elif event in (
                'fork', 'member', 'membership', 'page_build', 'team_add',
                'watch', 'status'):
            # print('Got ignored event "{}"'.format(event))
            return
        else:
            print('Got unknown event "{}"'.format(event))
            return

        if repo.startswith('kivy/'):
            repo = repo[5:]
        repo = color(COLOR_REPO, '[{}]'.format(repo))
        user = color(COLOR_USER, user)
        if issue:
            issue = color(COLOR_ISSUE, ' #{}'.format(issue))
        body = color(DEFAULT_COLOR, '* ' + self.shorten(body) + ' -')
        action = color(DEFAULT_COLOR, action)
        url = color(COLOR_URL, self.get_short_url(url), url=True)
        if target:
            target = color(DEFAULT_COLOR, ' {}'.format(target))

        res = '{}{} {} {}{} {} {}'.format(
            repo, target, user, action, issue, body, url)
        self.publish_message(res)

    def kgb_process_travis(self, repo, content):
        result = content['result_message']
        if content['type'] == 'pull_request' or result not in (
                'Passed', 'Fixed', 'Broken', 'Failed', 'Still Failing'):
            return

        key = (repo, content['branch'])
        if repo_status[key] == result and result == 'Passed':
            return
        repo_status[key] = result

        repo = color(COLOR_REPO, '[{}]'.format(repo))
        branch = color(DEFAULT_COLOR, content['branch'])
        result = color(
            PASS_COLOR if result == 'Passed' or result == 'Fixed' else
            FAIL_COLOR, '{}, build #{}'.format(result, content['number']))
        url = color(COLOR_URL, self.get_short_url(content['build_url']))
        body = color(DEFAULT_COLOR, '* ' + self.shorten(content['message']) + ' -')

        msg = '{}: {} {} {} {}'.format(result, repo, branch, body, url)
        self.publish_message(msg)

    def publish_message(self, text):
        for name in self.chans:
            self.serv.privmsg(name, text)


kgb = KGB(
    SERVERS,
    NICKNAME,
    'Show events from github')


#
# WEB part
#

app = Flask(__name__)


@app.route('/orgevent', methods=['POST'])
def pubsubhub():
    try:
        request.get_data()
        hashed = hmac.new(GITHUB_SECRET, request.data, sha1)
        signature = hashed.hexdigest()
        rqst_sig = request.headers.get('X-Hub-Signature', '')[5:]

        if rqst_sig != signature:
            print(
                "calculated signature \"{}\" doesn't match request signature "
                "\"{}\"".format(signature, rqst_sig))
            abort(401)

        kgb.treat_signal_hub(request.headers.get('X-GitHub-Event'), loads(request.form['payload']))
    except Exception as e:
        print('Got exception {}'.format(e))
        import traceback
        traceback.print_exc()
        raise
    return ''


@app.route('/travisevent', methods=['POST'])
def pubtravishub():
    try:
        request.get_data()
        repo = request.headers.get('Travis-Repo-Slug', '')
        signature = sha256(repo + TRAVIS_TOKEN).hexdigest()
        rqst_sig = request.headers.get('Authorization')
        if rqst_sig != signature:
            print(
                "Travis calculated signature \"{}\" doesn't match request signature "
                "\"{}\"".format(signature, rqst_sig))
            print('For {}'.format(repo))
            abort(401)

        kgb.kgb_process_travis(repo, loads(request.form['payload']))
    except Exception as e:
        print('Travis - Got exception {}'.format(e))
        import traceback
        traceback.print_exc()
        raise
    return ''


if __name__ == '__main__':
    p = Thread(target=kgb.start)
    p.daemon = True
    p.start()
    app.run(host='0.0.0.0', use_reloader=False)
