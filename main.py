#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import TrisApi
from utils import get_by_urlsafe
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every day using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)

        for user in users:
            games = Game.query(ndb.OR(Game.user1 == user.key,
                                      Game.user2 == user.key)). \
                filter(Game.game_over == False)
            if games.count() > 0:
                subject = 'Reminder for you!'
                body = 'Hello {}, you have games in progress'.format(user.name)
                # This will send test emails, the arguments to send_mail are:
                #  from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateAverageMovesPerGame(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        TrisApi._cache_average_moves_per_game()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_moves_per_game', UpdateAverageMovesPerGame),
], debug=True)
