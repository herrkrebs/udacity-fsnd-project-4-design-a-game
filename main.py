#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
from itertools import groupby

import webapp2
from google.appengine.api import mail, app_identity

from models.game import Game, GameState
from models.user import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()

        users = User.query()
        for user in users:
            games = Game.query(Game.active_player == user.key).filter(
                Game.state == GameState.ACTIVE)

            if games:
                subject = 'This is a reminder!'
                body = 'Hello {}, it\'s your turn!'.format(
                    user.name)

                # This will send notification emails,
                # the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
