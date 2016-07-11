# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from protorpc import remote, messages
from google.appengine.ext import ndb

from models import User, Game, GameState, UserRanking
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm, \
    ActiveGamesForm, GameMoveHistoryForm, UserRankingsForm, GameMoveHistory
from utils import get_by_urlsafe, number_of_won_games

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1)
)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1)
)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2)
)

CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1)
)

GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
    player_name=messages.StringField(1)
)

GET_USER_RANKINGS_REQUEST = endpoints.ResourceContainer(

)

GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1)
)


@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        player_one = User.query(User.name == request.player_one_name).get()
        if not player_one:
            raise endpoints.NotFoundException(
                'A User with that name {} does not exist!'.format(
                    request.player_one_name))

        player_two = User.query(User.name == request.player_two_name).get()
        if not player_two:
            raise endpoints.NotFoundException(
                'A User with that name {} does not exist!'.format(
                    request.player_two_name))

        game = Game.new_game(player_one.key, player_two.key)

        return game.to_form('Good luck playing Tic-Tac-Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.is_game_over():
            return game.to_form('Game already over!')

        x = request.x
        y = request.y
        player = User.query(User.name == request.player_name).get()

        if not player:
            raise endpoints.NotFoundException(
                'A player with the name {} doesn\'t exist'.format(
                    request.player_name))

        if not game.is_active_player(player):
            return game.to_form('It\'s not your turn!')

        if not game.is_field_empty(x, y):
            return game.to_form('Field at [{}][{}] is not empty!'.format(x, y))

        game.place_token(x, y)

        if game.has_active_player_won():
            game.won()
            return game.to_form('You win!')

        if game.is_board_full():
            game.tie()
            return game.to_form('Game is a tie!')

        game.put()
        return game.to_form('Token placed at [{}][{}]!'.format(x, y))

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.is_game_over():
            return game.to_form('You can\'t cancel an already finished game')

        game.cancel()

        return game.to_form('The game has been cancelled!')

    @endpoints.method(request_message=GET_USER_GAMES_REQUEST,
                      response_message=ActiveGamesForm,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all active games of the user"""
        player = User.query(User.name == request.player_name).get()

        games = Game.query(Game.state == GameState.ACTIVE)
        games = games.filter(ndb.OR(Game.player_one == player.key,
                                    Game.player_two == player.key))

        return ActiveGamesForm(
            games=[g.key.urlsafe() for g in games])

    @endpoints.method(request_message=GET_USER_RANKINGS_REQUEST,
                      response_message=UserRankingsForm,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns the rankings of all players"""
        players = User.query()
        rankings = [(number_of_won_games(player), player.name) for player in
                    players]
        rankings.sort(key=lambda ranking: ranking[0], reverse=True)

        return UserRankingsForm(
            rankings=[UserRanking(position=index + 1, wins=ranking[0],
                                  player_name=ranking[1]) for index, ranking in
                      enumerate(rankings)])

    @endpoints.method(request_message=GET_GAME_HISTORY_REQUEST,
                      response_message=GameMoveHistoryForm,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns the move history of the given game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        return GameMoveHistoryForm(histories=[
            GameMoveHistory(player_name=move['player'], x=move['x'],
                            y=move['y']) for move in game.history])


api = endpoints.api_server([TicTacToeApi])
