from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from pymongo import Connection
from pymongo.errors import ConnectionFailure
from weibo import APIClient
import time
import json
import pickle

APP_KEY = '1969610127'
APP_SECRET = '859a989986363a2e0fb2bb7ec86335a5'
CALLBACK = '/key/callback/'
TOKEN_FILE = 'access_token.pickle'

def key(request):
    """
    show the sinaweibo's access token expired data,
    if such token doesn't exist, redirect to 'key_gen' view
    to generate the token
    """
    try:
        pickle_file = open(TOKEN_FILE, 'rb')
        data = pickle.load(pickle_file)
        expires_time = time.ctime(data['expires_in'])
    except:
        return redirect("/key/gen/")
    return render(request, "show_key.html", {"expires_time":expires_time})

def key_gen(request):
    callback_uri = "http://%s%s" % (request.META['HTTP_HOST'], CALLBACK)
    client = APIClient(APP_KEY, APP_SECRET, callback_uri)
    return redirect(client.get_authorize_url())

def key_callback(request):
    code = request.GET['code']
    callback_uri = "http://%s%s" % (request.META['HTTP_HOST'], CALLBACK)
    client = APIClient(APP_KEY, APP_SECRET, callback_uri)
    r = client.request_access_token(code)
    client.set_access_token(r.access_token, r.expires_in)
    pickle_file = open(TOKEN_FILE, 'wb')
    pickle.dump({
        "access_token":r.access_token,
        "expires_in":r.expires_in
        },pickle_file)
    return redirect('/key/')

@csrf_exempt
def upload_courses(request):
    if request.method != 'POST':
        return HttpResponse(status=404)
    if 'user' not in request.POST or 'courses' not in request.POST:
        return HttpResponse(status=400)
    user = json.loads(request.POST['user'])
    courses = json.loads(request.POST['courses'])
    user_name = user['screen_name']
    try:
        connection = Connection()
    except ConnectionFailure, ex:
        error = {"code":0, "reason":"connection is to busy"}
        return HttpResponse(content=json.dumps(error),
                mimetype="application/json")
    db = connection['bjtu_courses']
    if not db.users.find_one({'id':user['id']}):
        db.users.save(user, safe=True)
    for c in courses:
        course = db.courses.find_one({'cid':c['cid'], 'order':c['order']})
        if course:
            if user_name not in course['students']:
                course['students'].append(user_name)
                db.courses.save(course, safe=True)
        else:
            c['students'] = [user_name]
            db.courses.save(c, safe=True)
    return HttpResponse(content=json.dumps({"code":1}))

