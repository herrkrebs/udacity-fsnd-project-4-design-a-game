"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import json
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class GameState(messages.Enum):
    """The state of a game"""
    ACTIVE = 0
    WON = 1
    TIE = 2
    CANCELLED = 3


class Game(ndb.Model):
    """Game object"""

    EMPTY_TOKEN = ' '
    PLAYER_ONE_TOKEN = 'X'
    PLAYER_TWO_TOKEN = 'O'

    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(required=True, kind='User')
    active_player = ndb.KeyProperty(required=True, kind='User')
    board = ndb.JsonProperty(required=True)
    state = msgprop.EnumProperty(GameState, required=True)
    history = ndb.PickleProperty(required=True, default=[])

    @classmethod
    def new_game(cls, player_one, player_two):
        """Creates and returns a new game"""
        game = Game(player_one=player_one,
                    player_two=player_two,
                    active_player=player_one,
                    board=[[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                    state=GameState.ACTIVE)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_one_name = self.player_one.get().name
        form.player_two_name = self.player_two.get().name
        form.board = self.board_to_string()
        form.game_state = str(self.state)
        form.message = message
        return form

    def board_to_string(self):
        return '{}|{}|{}\n-----\n{}|{}|{}\n-----\n{}|{}|{}' \
            .format(self.board[0][0],
                    self.board[0][1],
                    self.board[0][2],
                    self.board[1][0],
                    self.board[1][1],
                    self.board[1][2],
                    self.board[2][0],
                    self.board[2][1],
                    self.board[2][2])

    def is_game_over(self):
        return self.state != GameState.ACTIVE

    def won(self):
        """Ends the game"""
        self.state = GameState.WON
        self.put()

    def tie(self):
        """Sets the state of the game to a tie"""
        self.state = GameState.TIE
        self.put()

    def cancel(self):
        """Cancels the game"""
        self.state = GameState.CANCELLED
        self.put()

    def is_active_player(self, player):
        """Checks if the player is active"""
        return player.key == self.active_player

    def is_field_empty(self, x, y):
        """Checks if the field on the board is empty"""
        return self.board[x][y] == self.EMPTY_TOKEN

    def place_token(self, x, y):
        """Places the players token on the board"""
        self.board[x][y] = self.get_active_player_token()
        self.update_history(x, y)
        self.switch_active_player()

    def get_active_player_token(self):
        """Returns the token for the active player"""
        if self.active_player == self.player_one:
            return self.PLAYER_ONE_TOKEN

        return self.PLAYER_TWO_TOKEN

    def update_history(self, x, y):
        """Updates the game history"""
        player = self.active_player.get()
        move = {
            'player': player.name,
            'x': x,
            'y': y
        }

        self.history.append(move)

    def switch_active_player(self):
        if self.active_player == self.player_one:
            self.active_player = self.player_two
        else:
            self.active_player = self.player_one

    def is_board_full(self):
        return len(self.history) == 9

    def has_active_player_won(self):
        """Checks if the game is finished"""
        token = self.get_active_player_token()

        return (self.board[0][0] == self.board[0][1] == self.board[0][
            2] == token) or (
                   self.board[1][0] == self.board[1][1] == self.board[1][
                       2] == token) or (
                   self.board[2][0] == self.board[2][1] == self.board[2][
                       2] == token) or (
                   self.board[0][0] == self.board[1][1] == self.board[2][
                       2] == token) or (
                   self.board[0][2] == self.board[1][1] == self.board[2][
                       0] == token)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player_one_name = messages.StringField(2, required=True)
    player_two_name = messages.StringField(3, required=True)
    board = messages.StringField(4, required=True)
    game_state = messages.StringField(5, required=True)
    message = messages.StringField(6, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player_one_name = messages.StringField(1, required=True)
    player_two_name = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    player_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2, required=True)
    y = messages.IntegerField(3, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class ActiveGamesForm(messages.Message):
    """All active games for a user"""
    games = messages.StringField(1, repeated=True)


class GameMoveHistory(messages.Message):
    """A players move in a game"""
    player_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2, required=True)
    y = messages.IntegerField(3, required=True)


class GameMoveHistoryForm(messages.Message):
    """History of moves of a game"""
    histories = messages.MessageField(GameMoveHistory, 1, repeated=True)


class UserRanking(messages.Message):
    """A user ranking"""
    position = messages.IntegerField(1, required=True)
    player_name = messages.StringField(2, required=True)
    wins = messages.IntegerField(3, required=True)


class UserRankingsForm(messages.Message):
    """Represents a list of user rankings"""
    rankings = messages.MessageField(UserRanking, 1, repeated=True)
