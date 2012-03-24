from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import Connection
from pymongo.errors import ConnectionFailure
import json
import pickle

def key(request):
    pickle_file = open('access_token.pickle', 'r') 
    data = pickle.load(pickle_file)
    return HttpResponse("%s : %s" % (data['access_token'], data['expires_in']))

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

