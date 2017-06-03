import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

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
                        logger.debug(question.answer)
                        if str(reply['payload']) == str(question.answer):
                            correctness = True
                            reply = 'right' + str(message['sender']['id'])
                        else:
                            correctness = False
                            reply = 'wrong' + str(message['sender']['id'])
                        user = users.get_user(
                            im_type='fb',
                            im_id=str(message['sender']['id']),
                        )
                        user.save_answer(
                            question=question,
                            correctness=correctness,
                        )
                        post_facebook_message(
                            message['sender']['id'],
                            reply,
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
                    if message['postback']['payload'] == 'register_user':
                        logger.debug('register_user')
                        post_facebook_message(
                            message['sender']['id'], 'register_user'
                        )
                    elif message['postback']['payload'] == 'exit':
                        logger.debug('exit')
                        post_facebook_message(
                            message['sender']['id'], 'exit'
                        )
                    else:
                        user = users.get_user(
                            im_type='fb',
                            im_id=str(message['sender']['id']),
                        )
                        try:
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
                        except:
                            post_facebook_message(
                                message['sender']['id'],
                                "not_exist_" + str(message['sender']['id']),
                            )
        return HttpResponse()


fb_webhook = FacebookWebhookView.as_view()
