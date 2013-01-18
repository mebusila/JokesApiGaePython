import webapp2
from models import *
import json
import cgi
from datetime import datetime
from random import randint
from google.appengine.api import memcache

class JokesListHandler(webapp2.RequestHandler):
    def get(self):
        try:
            limit = int(self.request.get('limit'))
        except :
            limit = 10
        try:
            offset = int(self.request.get('offset'))
        except :
            offset = 0
        try:
            tags = self.request.get_all('tags')
        except:
            tags = None

        cache_key = 'jokes/%s/%s/%s' % (limit, offset, "-".join(tags))
        items = memcache.get(cache_key)
        if items == None:
            q = Joke.all()
            for tag in tags:
                q.filter('tags IN', [tag])
            items = q.fetch(limit, offset = offset)
            memcache.add(cache_key, items, 600)
        jokes = []
        for item in items:
            jokes.append(item)
        self.response.write(
            json.dumps(
                [joke.to_dict() for joke in jokes]
            )
        )

    def post(self):
        content = self.request.get_all('content')
        if not content:
            return self.error(400)
        tags = self.request.get_all('tags')
        joke = Joke(content = content, updated_at = datetime.now(), tags = tags).put()
        if joke:
            return self.response.set_status(201)
        return self.error(400)

class JokesRandomHandler(webapp2.RequestHandler):
    def get(self):
        try:
            count = int(self.request.get('count'))
        except :
            count = 10
        try:
            tags = self.request.get_all('tags')
        except:
            tags = None

        q = Joke.all()

        for tag in tags:
            q.filter('tags IN', [tag])

        total = memcache.get('jokes/count')
        if total == None:
            total = q.count()
            memcache.add('jokes/count', total, 3600)
        if total < count:
            offset = 0
        else:
            offset = randint(1, int(total - count))
        items = q.fetch(count, offset = offset)
        jokes = []
        for item in items:
            jokes.append(item)
        self.response.write(
            json.dumps(
                [joke.to_dict() for joke in jokes]
            )
        )

class JokeHandler(webapp2.RequestHandler):
    def get(self, joke_id):
        try:
            joke = Joke.get_by_id(int(joke_id))
            if joke == None:
                return self.error(404)
            return self.response.write(
                    json.dumps(
                        joke.to_dict()
                    )
            )
        except:
            return self.error(404)

app = webapp2.WSGIApplication([
    ('/api/jokes/random', JokesRandomHandler),
    ('/api/jokes/(\d+)', JokeHandler),
    ('/api/jokes', JokesListHandler)
], debug=True)
