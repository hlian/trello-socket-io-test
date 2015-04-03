from __future__ import print_function, unicode_literals

import json
import requests
import sys
import thread
import websocket

SUBSCRIBE = """
3:::{"appKey":"%s","reqid":"3767700026","rgarg":["%s"],"sFxn":"subscribeToBoard","token":"%s"}
""".strip()

def http_for_wsid(site):
    url = '%s/socket.io/1/' % site
    response = requests.get(url)
    assert response.status_code == 200, response.content
    return int(response.content.split(':')[0])

def http_for_token(site, appkey, user, password):
    url = '%s/1/login' % site
    params = {
        'user': user,
        'password': password,
        'appKey': appkey,
        'expiration': 'never',
        'scope': 'read,write,account',
        'identifier': 'Trello for iOS',
    }
    response = requests.post(url, data=params)
    assert response.status_code == 200, response.content
    j = json.loads(response.content)
    return j['token']

def http_for_board_id(site, appkey, token):
    url = '%s/1/members/me' % site
    params = {
        'key': appkey,
        'token': token,
        'boards': 'open'
    }
    response = requests.get(url, params=params)
    assert response.status_code == 200, response.content
    j = json.loads(response.content)
    return j['idBoards'][0]

def debug(*a, **kw):
    print(a)

def main(site, appkey, user, password):
    wsid = http_for_wsid(site)
    token = http_for_token(site, appkey, user, password)
    board_id = http_for_board_id(site, appkey, token)

    def run():
        msg = SUBSCRIBE % (appkey, board_id, token)
        print('>> sending: %s' % msg)
        ws.send(msg)
        print('>> sent!')
    def on_open(ws):
        thread.start_new_thread(run, ())

    url = '%s/socket.io/1/websocket/%s' % (site, wsid)
    url = url.replace('http', 'ws')
    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=debug, on_error=debug, on_close=debug)
    ws.run_forever()

if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.stderr.write('USAGE: python %@ [site e.g. "https://trellis.coffee"] [appkey] [username] [password]')
        sys.stderr.write('\n')
        sys.exit(1)
    site = sys.argv[1]
    appkey = sys.argv[2]
    user = sys.argv[3]
    password = sys.argv[4]
    main(site, appkey, user, password)
