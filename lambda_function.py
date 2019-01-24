"""
AWS lambda code for guess Them Avengers
"""

from __future__ import print_function
from helpScript import avengers, avengerHint, voices
import random

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak> "+output+" </speak>"
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_guessIntent_response(intent, session):
    card_title = "Guess"
    should_end_session = False

    loudEmphasis = '<prosody volume="x-loud">{text}</prosody>'
    sayAs = '<say-as interpret-as="interjection">{text}</say-as>'

    session_attributes = session['attributes']
    print(session_attributes)
    userInput = intent['slots']['avengerName']['resolutions']['resolutionsPerAuthority'][0]

    userInputStatus = userInput['status']['code']
    matchedCode = "ER_SUCCESS_MATCH"

    if userInputStatus == matchedCode:
        userInputValues = userInput['values'][0]['value']
        guessedAvenger = int(userInputValues['id'])
        chosenAvenger = session_attributes['chosenAvenger']
        print(chosenAvenger)

        if guessedAvenger == chosenAvenger:
            speech_output = loudEmphasis.format(text='Correct Answer!')+" You've been watching Marvel closely. Hope to see you loose next time!"
            reprompt_text = "Great Guess! You won't be so lucky next time though."
            should_end_session = True
        elif not session_attributes['confirming']:
            speech_output = "You think it's {guessedAvengerName}?.".format(guessedAvengerName = loudEmphasis.format(text=avengers[guessedAvenger]))
            reprompt_text = "You really think it's {guessedAvengerName}?.".format(guessedAvengerName = avengers[guessedAvenger])
            session_attributes['confirming'] = True
        else:
            speech_output = loudEmphasis.format(text="Have you actually watched any Marvel movie?")+" That's an Incorrect Answer. Watch some movies and come back again!"
            reprompt_text = "Seriously. Watch some Marvel movies. They're great!"
            should_end_session = True
    else:
        guessedAvenger = 0
        speech_output = "I don't think I know him, or her."
        reprompt_text = "Really, Don't know him."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_repeatIntent_response(intent, session):
    card_title = "Repeat"
    session_attributes = session['attributes']
    chosenAvenger = session_attributes['chosenAvenger']
    chosenHint = session_attributes['chosenHint']
    repeatHint = avengerHint[chosenAvenger][chosenHint]
    reducedEmphasis = '<emphasis level="reduced">{text}</emphasis>'
    modEmphasis = '<emphasis level="moderate">{text}</emphasis>'
    speech_output = reducedEmphasis.format(text='Yeah, here it is.') + ' <break time="1s"/> ' + modEmphasis.format(text=repeatHint)
    reprompt_text = "I'll repeat again. "+repeatHint
        
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = """Welcome!, Oh Wait. We don't do that here. So! Let's see what you've got. Here's your hint. <break time="1s"/>"""

    totalAvengers = len(avengers)
    chosenAvenger = random.randint(0,totalAvengers-1)

    totalHints = len(avengerHint[chosenAvenger])
    chosenHint = random.randint(0,totalHints-1)

    session_attributes['chosenAvenger'] = chosenAvenger
    session_attributes['chosenHint'] = chosenHint
    session_attributes['confirming'] = False

    modEmphasis = '<emphasis level="moderate">{text}</emphasis>'
    speech_output += '<voice name="{voice}">{text}</voice>'.format(text=avengerHint[chosenAvenger][chosenHint], voice=voices[chosenAvenger])
    #speech_output += modEmphasis.format(text=avengerHint[chosenAvenger][chosenHint])
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I'll repeat. "+avengerHint[chosenAvenger][chosenHint]
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    modEmphasis = '<emphasis level="moderate">{text}</emphasis>'
    endgame = modEmphasis.format(text='Endgame!')
    speech_output = "Thank you for trying me out. " + endgame
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific 
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass

    

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "guessIntent":
        return get_guessIntent_response(intent, session)
    elif intent_name == "repeatIntent":
        return get_repeatIntent_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #    raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])