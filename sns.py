import weibo
import time
import pickle

def log(text):
    f = open('weibo.log', 'a+')
    f.write('%s\t%s' % 
            (time.strftime("%Y-%m-%d %H:%M:%S"), text.encode('utf-8')))
    f.write('\n')
    f.close()

class WeiboClient:
    def __init__(self):
        APP_KEY = '1969610127'
        APP_SECRET = '859a989986363a2e0fb2bb7ec86335a5'
        self.client = weibo.APIClient(app_key=APP_KEY, app_secret=APP_SECRET)
        pickle_file = open('access_token.pickle', 'rb')
        data = pickle.load(pickle_file)
        self.client.set_access_token(data['access_token'], data['expires_in'])

    def send_status(self, status):
        log(status)
        if not self.client.is_expires():
            self.client.post.statuses__update(status=status)

