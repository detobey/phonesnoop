# -------------------------------------------------#
# Title: Phone Snoop
# Dev:   David Tobey
# Date:  10/11/2017
# ChangeLog: (Who, When, What)
# 10/11/2017: Psuedo Code
# 10/17/2017: reputation_level and belongs_to is
#   working. Add adjective selector for rep level
#   (eg, 1 'rated highly trustworthy').
#   Must also add address data.
# 11/07/2017: populate templates yaml with new questions, statements
# -------------------------------------------------#

#### Summary
""" This skill accepts a 10-digit US phone number from a user and returns the
caller ID and reliability rating from the WhitePages API. """

#### Directives
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

#### Skill Metadata
app = Flask(__name__)
ask = Ask(app, "/")

#### Classes & Methods
@ask.intent("snoop",
            mapping={'user_phone': 'Number'})
def snoop(user_phone):

    '''Interestingly, this variable is not passed to the 'snoop' method when
    defined outside the method itself.'''
    api_file = open('/home/ubuntu/code/resc/api_key.txt', 'r')
    api_key = api_file.read().replace('WHITEPAGES=', '').rstrip()

    if int(user_phone[:1]) != 1 and len(str(user_phone)) != 10 or int(
            user_phone[:1]) == 1 and len(str(user_phone)) != 11:
        return question(render_template('excess_digits'))

    try:
        raw_level = requests.get(
            'https://proapi.whitepages.com/3.0/phone_reputation?phone=' +
            str(user_phone) + '&api_key=' + str(api_key))
        snoop_level = raw_level.json()
        rep_level = snoop_level['reputation_level']

    except requests.exceptions.RequestException as level_error:
        return question(level_error)

    try:
        raw_reverse = requests.get(
            'https://proapi.whitepages.com/3.0/phone?phone=' +
            str(user_phone) + '&api_key=' + str(api_key))
        raw_reverse = raw_reverse.json()
        belongs_to = raw_reverse['belongs_to'][1-1]['name'],'of',\
                     raw_reverse['current_addresses'][1-1]['street_line_1'],\
                     raw_reverse['current_addresses'][1-1]['city'],\
                     raw_reverse['current_addresses'][1-1]['state_code'],\
                     raw_reverse['current_addresses'][1-1]['postal_code']

    except requests.exceptions.RequestException as reverse_error:
        return question(reverse_error)

    if raw_reverse['belongs_to'] == []:
        return question(user_phone + ' is rated as ' + str(
            rep_level) +'. It is an unlisted number.')

    else:
        return question(user_phone + ' is rated as ' + str(rep_level)
                        + '. It belongs to ' + str(belongs_to) + '.')

@ask.intent('AMAZON.StopIntent')
def handle_stop():
    stop_cancel = render_template('stop_cancel')
    return statement(stop_cancel)

@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    stop_cancel = render_template('stop_cancel')
    return statement(stop_cancel)

@ask.intent('AMAZON.HelpIntent')
def handle_help():
    greeting_help = render_template('help')
    return question(greeting_help)

#### Main
if __name__ == "__main__":
    app.config['ASK_VERIFY_REQUESTS'] = False
    app.run()










