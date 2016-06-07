# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, GameForms, MakeMoveForm,\
    ScoreForms, EmailPreferenceForm, RankingForm
from utils import get_by_urlsafe


import collections
import operator

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2),
                                           email_remainder=messages.BooleanField(3))
NEW_EMAIL_PREFERENCE_REQUEST = endpoints.ResourceContainer(urlsafe_user_key=messages.StringField(1),
                                           email=messages.StringField(2),
                                           email_remainder=messages.BooleanField(3))
GET_EMAIL_PREFERENCE_REQUEST = endpoints.ResourceContainer(
        urlsafe_user_key=messages.StringField(1),)

MEMCACHE_AVERAGE_MOVES_PER_GAME = 'AVERAGE_MOVES_PER_GAME'

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
        user = User(name=request.user_name, email=request.email, email_remainder=request.email_remainder)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_EMAIL_PREFERENCE_REQUEST,
                      response_message=EmailPreferenceForm,
                      path='user/{urlsafe_user_key}',
                      name='set_email_remainder',
                      http_method='POST')
    def set_email_preference(self, request):
        """Set the email preference for the user"""
        user = get_by_urlsafe(request.urlsafe_user_key, User)
        if not user:
            raise endpoints.ConflictException(
                    'A User with that name does not exist!')
        if request.email:
            user.email = request.email
        if request.email_remainder:
            user.email_remainder = request.email_remainder
        user.put()
        return user.email_form()

    @endpoints.method(request_message=GET_EMAIL_PREFERENCE_REQUEST,
                      response_message=EmailPreferenceForm,
                      path='user/{urlsafe_user_key}',
                      name='get_email_remainder',
                      http_method='GET')
    def get_email_remainder(self, request):
        """Get the email preference for the user"""
        user = get_by_urlsafe(request.urlsafe_user_key, User)
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        return user.email_form()

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user1 = User.query(User.name == request.user_name1).get()
        if not user1:
            raise endpoints.NotFoundException(
                    'User1 with that name does not exist!')
        user2 = User.query(User.name == request.user_name2).get()
        if not user2:
            raise endpoints.NotFoundException(
                    'User2 with that name does not exist!')

        game = Game.new_game(user1.key, user2.key)
        return game.to_form('Have fun playing Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.moves % 2 == 0 :
                return game.to_form('It is player1 {} to make a move!'.format(game.user1.get().name))
            else:
                return game.to_form('It is player2 {} to make a move!'.format(game.user2.get().name))
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='GET')
    def cancel_game(self, request):
        """Deletes the game, if it is unfished."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            raise endpoints.ConflictException('Game is already over, therefore cannot be deleted!')
        game.key.delete()
        return StringMessage(message='Game {} has been deleted!'.format(
                request.urlsafe_game_key))

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return the state for all games for the provided user."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(ndb.OR(Game.user1 == user.key, Game.user2 == user.key))
        game_forms = list()
        for game in games:
            if game.moves % 2 == 0:
                game_forms.append(game.to_form('It is player1 {} to make a move!'.format(game.user1.get().name)))
            else:
                game_forms.append(game.to_form('It is player2 {} to make a move!'.format(game.user2.get().name)))
        return GameForms(game_forms=game_forms)

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            if game.user1_won:
                return game.to_form('Game already over! Player 1 Won')
            elif game.user2_won:
                return game.to_form('Game already over! Player 2 Won')
            else:
                return game.to_form('Game already over! It is a draw')

        previous_board_position = game.board_position.split(',')
        new_board_position = request.move.split(',')

        validation = TicTacToeApi._validate_board_position(new_board_position,
            previous_board_position)
        if validation.valid == False:
            return game.to_form(validation.message)

        response_message = validation.message

        if TicTacToeApi._check_for_win(new_board_position, 'X'):
            response_message = "Player 1 won!"
            game.end_game(user1_won=True,
                user2_won=False,
                user1_lost=False,
                user2_lost=True)
        elif TicTacToeApi._check_for_win(new_board_position, 'O'):
            response_message = "Player 2 won!"
            game.end_game(user1_won=False,
                user2_won=True,
                user1_lost=True,
                user2_lost=False)
        elif game.moves == 9:
            response_message = "It is a draw!"
            game.end_game(user1_won=False,
                user2_won=False,
                user1_lost=False,
                user2_lost=False)

        game.board_position = request.move
        game.moves = game.moves + 1
        game.put()

        if game.game_over:
            taskqueue.add(url='/tasks/cache_average_moves_per_game')

        return game.to_form(response_message)

    @staticmethod
    def _validate_board_position(new_board_position, previous_board_position):
        """Validates the board position and the move"""
        Validation = collections.namedtuple('Validation', ['valid', 'message'])

        # check that the input is correct
        num_of_empty = 0
        num_of_Xs = 0
        num_of_Os = 0
        if len(new_board_position) != 9:
            return Validation(False, 'Invalid input! Input should be 9 comma seperated chars')
        else:
            for pos in new_board_position:
                print pos
                if (pos != "-" and pos != 'X' and pos != 'O'):
                    return Validation(False, "Invalid input. Chars should be '-', 'X', or 'O'")
                elif pos == 'X':
                    num_of_Xs = num_of_Xs + 1
                elif pos == 'O':
                    num_of_Os = num_of_Os + 1
                elif pos == '-':
                    num_of_empty = num_of_empty + 1

            if num_of_Xs - num_of_Os == 2:
                return Validation(False,
                    "Not your turn. It is player 2\'s turn to play an 'O'!")
            elif num_of_Xs - num_of_Os == -1:
                return Validation(False,
                    "Not your turn. It is player 1\'s turn to play a 'X'!")

        # check that the move is valid
        num_of_differences = 0
        for pos_ind in range(0,len(new_board_position)):
            if (previous_board_position[pos_ind] != '-'
                and previous_board_position[pos_ind] != new_board_position[pos_ind]):
                    return Validation(False, 'Invalid move!')
            elif previous_board_position[pos_ind] != new_board_position[pos_ind]:
                num_of_differences = num_of_differences + 1
        if num_of_differences != 1:
            return Validation(False, 'Invalid move!')

        if (num_of_empty == 0):
            return Validation(True, 'It is a draw! Game Over')
        elif num_of_Xs == num_of_Os:
            return Validation(True, 'It is player 1\'s turn now')
        else:
            return Validation(True, 'It is player 2\'s turn now')

    @staticmethod
    def _check_for_win(board_position, player_piece):
        win_cond = ((1,2,3), (4,5,6), (7,8,9), (1,4,7), (2,5,8), (3,6,9), (1,5,9), (3,5,7))

        for each in win_cond:
            try:
                if(board_position[(each[0]-1) * 3] == player_piece and board_position[(each[1]-1) * 3] == player_piece and board_position[(each[2]-1) * 3] == player_piece):
                    print board_position[each[0]-1]
                    win = True
                else:
                    win = False
            except:
                pass
        return win

    @endpoints.method(response_message=ScoreForms,
                  path='scores',
                  name='get_scores',
                  http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=RankingForm,
                      path='scores/user/{user_name}/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns an individual User's ranking"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query()
        user_to_stats = {}
        wins = 0
        losses = 0
        for score in scores:
            if score.user not in user_to_stats:
                user_to_stats[score.user] = {'wins':0, 'losses':0, 'games':0}
            if score.won == True:
                user_to_stats[score.user]['wins'] = user_to_stats[score.user]['wins'] + 1
            elif score.lost == True:
                user_to_stats[score.user]['losses'] = user_to_stats[score.user]['losses'] + 1
            user_to_stats[score.user]['games'] = user_to_stats[score.user]['games'] + 1

        # calculate the net_win_ratio
        user_to_ratio = {}
        for user in user_to_stats:
            user_to_ratio[user] = (user_to_stats[user]['wins'] - user_to_stats[user]['losses']) / float(user_to_stats[score.user]['games'])

        # rank users by ratio
        ranked_users = sorted(user_to_ratio, key=user_to_ratio.get, reverse=True)

        return RankingForm(user_name=request.user_name, rank=ranked_users.index(user) + 1, net_win_ratio=user_to_ratio[user])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_moves_per_game',
                      name='get_average_moves_per_game',
                      http_method='GET')
    def get_average_moves_per_game(self, request):
        """Get the cached average wins"""
        return StringMessage(message=memcache.get(MEMCACHE_AVERAGE_MOVES_PER_GAME)
            or 'Still computing this stat.')

    @staticmethod
    def _cache_average_moves_per_game():
        """Populates memcache with the average moves made in finished Games"""
        games = Game.query(Game.game_over == True).fetch()
        if games:
            count = len(games)
            total_moves = sum([game.moves for game in games])
            average = float(total_moves)/count
            memcache.set(MEMCACHE_AVERAGE_MOVES_PER_GAME,
                         'The average moves made in finsihed games is {:.2f}'.format(average))


api = endpoints.api_server([TicTacToeApi])