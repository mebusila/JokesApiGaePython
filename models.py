from google.appengine.ext import db

class Joke(db.Model):
    content = db.StringListProperty()
    tags = db.StringListProperty()

    def __unicode__(self):
        return self.content
    def to_dict(self):
        return db.to_dict(self, {'id':self.key().id()})