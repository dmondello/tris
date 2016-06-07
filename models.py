"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


    def email_form(self):
        form = EmailPreferenceForm()
        form.email = self.email
        return form

class Game(ndb.Model):
    """Game object"""
    board_position = ndb.StringProperty(required=True, 
        default="-,-,-,-,-,-,-,-,-")
    game_over = ndb.BooleanProperty(required=True, default=False)
    user1_won = ndb.BooleanProperty(required=True, default=False)
    user2_won = ndb.BooleanProperty(required=True, default=False)
    user1 = ndb.KeyProperty(required=True, kind='User')
    user2 = ndb.KeyProperty(required=True, kind='User')
    moves = ndb.IntegerProperty(required=True, default=0)

    @classmethod
    def new_game(cls, user1, user2):
        """Creates and returns a new game"""
        game = Game(user1=user1,
                    user2=user2)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name1 = self.user1.get().name
        form.user_name2 = self.user2.get().name
        form.board_position = self.board_position
        form.game_over = self.game_over
        form.message = message

        return form

    def end_game(self, user1_won, user2_won, user1_lost, user2_lost):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.user1_won = user1_won
        self.user2_won = user2_won
        # Add the game to the score 'board'
        score1 = Score(user=self.user1,date=date.today(), 
            won=user1_won, lost=user1_lost)
        score2 = Score(user=self.user2,date=date.today(), 
            won=user2_won, lost=user2_lost)
        score1.put()
        score2.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    lost = ndb.BooleanProperty(required=True)

    def to_form(self):
        print "self.won = " + str(self.won) 
        return ScoreForm(user_name=self.user.get().name, 
            date=str(self.date),
            won=self.won,
            lost=self.lost)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board_position = messages.StringField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name1 = messages.StringField(5, required=True)
    user_name2 = messages.StringField(6, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    game_forms = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name1 = messages.StringField(1, required=True)
    user_name2 = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    move = messages.StringField(1, required=True)


class RankingForm(messages.Message):
    """RankingForm for outbound Ranking information"""
    user_name = messages.StringField(1, required=True)
    rank = messages.IntegerField(2, required=True)
    net_win_ratio = messages.FloatField(3, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    lost = messages.BooleanField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

'''
class EmailPreferenceForm(messages.Message):
    """Used to set a new email preference"""
    email = messages.StringField(1)
    # @TODO DELETE
    # email_remainder = messages.BooleanField(2)
'''

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
