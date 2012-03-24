from weibo import APIClient
from django.shortcuts import redirect
import pickle

APP_KEY = '1969610127'                                                      
APP_SECRET = '859a989986363a2e0fb2bb7ec86335a5'
PROTOCOL = 'http'
DOMAIN = '127.0.0.1:8000'
CALLBACK = '/callback/'
CALLBACK_URI = '%s://%s%s' % (PROTOCOL, DOMAIN, CALLBACK)

class OAuth2Middleware:
    def __init__(self):
        self.client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URI)
        self.request_uri = None

    def process_request(self, request):
        if request.path == CALLBACK:
            code = request.GET['code']
            r = self.client.request_access_token(code)
            self.client.set_access_token(r.access_token, r.expires_in)
            # save access_token
            output = open('access_token.pickle', 'w')
            pickle.dump({"access_token":r.access_token, "expires_in": r.expires_in}, output)
            return redirect(self.request_uri)
        if self.client.is_expires():
            self.request_uri = request.get_full_path()
            return redirect(self.client.get_authorize_url())
        return None
