"""user.py - Contains the user model and forms"""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class UserRanking(messages.Message):
    """A user ranking"""
    position = messages.IntegerField(1, required=True)
    player_name = messages.StringField(2, required=True)
    wins = messages.IntegerField(3, required=True)


class UserRankingsForm(messages.Message):
    """Represents a list of user rankings"""
    rankings = messages.MessageField(UserRanking, 1, repeated=True)