import json
import logging
from pprint import pprint

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.shortcuts import render

from quizzler import im, users

from .fb_api import post_facebook_message


logger = logging.getLogger(__name__)


class FacebookWebhookView(View):

    def get(self, request, *args, **kwargs):
        params = self.request.GET
        if params['hub.verify_token'] == settings.FACEBOOK_VERIFY_TOKEN:
            return HttpResponse(params['hub.challenge'])
        else:
            return HttpResponseBadRequest('Error, invalid token')

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    logger.debug('message')
                    if 'quick_reply' in message['message']:
                        reply = message["message"]["quick_reply"]
                        question = im.get_current_question(
                            im_type='fb', im_id=str(message['sender']['id'])
                        )
                        logger.debug('問題 1 答案： {}'.format(question.answer))
                        if str(reply['payload']) == str(question.answer).replace(u'\xa0', ' '):
                            correctness = True
                            reply = 'right_' + str(message['sender']['id'])
                        else:
                            correctness = False
                            reply = 'wrong_' + str(message['sender']['id'])
                        user = users.get_user(
                            im_type='fb',
                            im_id=str(message['sender']['id']),
                        )
                        user.save_answer(
                            question=question,
                            correctness=correctness,
                        )
                        #setting question
                        question = user.get_next_question()
                        logger.debug('問題 2 答案： {}'.format(question.answer))
                        im.set_current_question(
                            question=question,
                            im_type='fb',
                            im_id=str(message['sender']['id']),
                        )
                        post_facebook_message(
                            message['sender']['id'],
                            reply,
                            q=question
                        )
                    try:
                        post_facebook_message(
                            message['sender']['id'],
                            message['message']['text'],
                        )
                    except:
                        continue

                if 'postback' in message:
                    logger.debug('postback')
                    if message['postback']['payload'] == 'registeruser':
                        logger.debug('registeruser')
                        post_facebook_message(
                            message['sender']['id'], 'registeruser'
                        )
                    elif message['postback']['payload'] == 'exit':
                        logger.debug('exit')
                        post_facebook_message(
                            message['sender']['id'], 'exit'
                        )
                    elif message['postback']['payload'].split('_')[0] == '@@':
                        post_facebook_message(
                            message['sender']['id'],
                            'start_regist' + str(message['sender']['id'] + 
                            '*' + message['postback']['payload'].split('_')[1]
                            )
                        )
                    else:
                        try:
                            user = users.get_user(
                                im_type='fb',
                                im_id=str(message['sender']['id']),
                            )
                            #setting question
                            question = user.get_next_question()
                            logger.debug(question.answer)
                            im.set_current_question(
                                question=question,
                                im_type='fb',
                                im_id=str(message['sender']['id']),
                            )
                            post_facebook_message(
                                message['sender']['id'],
                                message['postback']['payload'],
                                q=question,
                            )
                        except users.UserDoesNotExist:
                            post_facebook_message(
                                message['sender']['id'],
                                "notexist_" + str(message['sender']['id']),
                            )
                        except Exception as e:
                            logger.debug(" @@ 發生錯誤: {}".format(str(e)))
                            post_facebook_message(
                                message['sender']['id'],
                                'error' + str(message['sender']['id']),
                            )
        return HttpResponse()


def leaderboard(request):
    leader_gen = users.generate_leaders()
    return render(request, 'leaderboard.html', {
        'leader_gen':leader_gen
    })


fb_webhook = FacebookWebhookView.as_view()
