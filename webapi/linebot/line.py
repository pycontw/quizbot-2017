import os
import re
import random
from urllib import parse as urlparse
from parse import parse
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackTemplateAction,
    MessageTemplateAction,
    PostbackEvent,
    CarouselTemplate,
    CarouselColumn,
)
from werkzeug.contrib.cache import SimpleCache

from quizzler import users
from quizzler import questions
from quizzler import im
from quizzler import registrations


store = SimpleCache(default_timeout=0)

line_bot_api = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))
line_webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

ACTION = 'a'
SELECT_TICKET = '0'

NICKNAME = 'Nickname (shown on ID card) / 暱稱 (顯示於識別證)'
SERIAL = '報名序號'
REGISTER = 'R'


def get_quizzler_user(user_id):
    try:
        return users.get_user(im_type='LINE', im_id=user_id)
    except users.UserDoesNotExist:
        return None


def get_message_for_next_question(user, event):
    question = user.get_next_question()
    im.set_current_question(
        question=question,
        im_type='LINE',
        im_id=event.source.user_id
    )

    choices = [question.answer, *question.wrong_choices]
    random.shuffle(choices)
    columns = [
        CarouselColumn(
            title=f'選項 {i}',
            text=choice[:60],
            actions=[
                MessageTemplateAction(label='選擇', text=f'您選擇了：{choice}')
            ]
        )
        for i, choice in enumerate(choices, 1)
    ]

    return [
        TextSendMessage(text=f'Q: {question.message}'),
        TemplateSendMessage(
            alt_text='Select answer',
            template=CarouselTemplate(
                columns=columns
            )
        )
    ]


class Replier(object):
    def __init__(self, event):
        self.event = event
        self.user_id = event.source.user_id
        try:
            self.user = users.get_user(im_type='line', im_id=self.user_id)
        except users.UserDoesNotExist:
            self.user = None
        if event.type == 'message':
            self.message = event.message.text.strip()
        elif event.type == 'postback':
            self.postback = event.postback.data

    def handle_begin_registration(self):
        im.activate_registration_session(im_type='line', im_id=self.user_id)
        return TextSendMessage(text='請輸入註冊的電子郵件')

    def handle_email_registration(self):
        info_list = registrations.get_registrations(email=self.message)
        if not info_list:
            return TextSendMessage(
                text='從報名資料裡找不到這個 email 耶，再輸入一次吧～'
            )
        else:
            identity_selections = [
                PostbackTemplateAction(
                    label=f'#{user[SERIAL]}, {user[NICKNAME]}'[:20],
                    data=f'{REGISTER}:{user.uid}',
                )
                for user in info_list
            ]
            return TemplateSendMessage(
                alt_text='選擇身份',
                template=ButtonsTemplate(
                    title='你是下面其中一個嗎？',
                    text='若不是，請選擇「取消」並重新輸入正確的 email',
                    actions=[
                        *identity_selections,
                        PostbackTemplateAction(
                            label='取消',
                            data=f'{REGISTER}:CANCEL'
                        )
                    ]
                )
            )

    def handle_select_identity(self):
        kktix_id = parse(f'{REGISTER}:{{kktix_id}}', self.postback)['kktix_id']
        if kktix_id != 'CANCEL':
            user = users.add_user_im(
                serial=kktix_id,
                im_type='line',
                im_id=self.user_id
            )
            im.complete_registration_session(
                im_type='line',
                im_id=self.user_id
            )
            return TextSendMessage(text=f'註冊完成 {user.serial}')
        else:
            return TextSendMessage(text=f'請輸入 email 以進行註冊：')


@line_webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    replier = Replier(event)

    if im.is_registration_session_active(im_type='line', im_id=replier.user_id):
        reply = replier.handle_email_registration()
    elif event.message.text == '註冊':
        reply = replier.handle_begin_registration()
    else:
        return

    line_bot_api.reply_message(event.reply_token, reply)


@line_webhook_handler.add(PostbackEvent)
def handle_postback(event):
    replier = Replier(event)
    if im.is_registration_session_active(im_type='line', im_id=replier.user_id):
        reply = replier.handle_select_identity()
    else:
        return

    line_bot_api.reply_message(event.reply_token, reply)


# @line_webhook_handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_id = event.source.user_id
#     user = get_quizzler_user(user_id)

#     if '/login' == event.message.text.strip():
#         if user is not None:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text='無效：您已經註冊過了')
#             )
#             return
#         line_bot_api.reply_message(
#             event.reply_token,
#             TemplateSendMessage(
#                 alt_text='Select ticket type',
#                 template=ButtonsTemplate(
#                     title='請選擇票種',
#                     text='請選擇您在 KKTIX 上註冊的票券的「活動名稱」：\n'
#                          '「PyCon Taiwan 2017 _____ / 活動報名」',
#                     actions=[
#                         PostbackTemplateAction(
#                             label=label,
#                             text='KKTIX 活動：「PyCon Taiwan 2017 '
#                                  f'{label} / 活動報名」',
#                             data=f'{ACTION}={SELECT_TICKET}&ticket={ticket}',
#                         )
#                         for ticket, label in [
#                             ('REG', 'Registration'), ('INV', 'Invitation')
#                         ]
#                     ]
#                 )
#             )
#         )

#     elif event.message.text.isdigit():
#         ticket, serial = store.get_many(
#             f'{user_id}.ticket',
#             f'{user_id}.serial'
#         )
#         if ticket is not None and serial is False:
#             serial = event.message.text
#             if user is not None:
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text='無效：您已經註冊過了')
#                 )
#                 return
#             else:
#                 user = users.add_user_im(ticket=ticket, serial=serial,
#                                          im_type='LINE', im_id=user_id)
#             store.delete_many(f'{user_id}.ticket', f'{user_id}.serial')
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 [
#                     TextSendMessage(text=f'註冊完成，開始遊戲！'),
#                     *get_message_for_next_question(user, event),
#                 ]
#             )

#     elif event.message.text.startswith('您選擇了：'):
#         try:
#             question = im.get_current_question(
#                 im_type='LINE',
#                 im_id=user_id
#             )
#         except im.CurrentQuestionDoesNotExist:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text='CurrentQuestionDoesNotExist'),
#             )
#             return
#         user_answer = event.message.text[len('您選擇了：'):]
#         if user_answer not in [question.answer, *question.wrong_choices]:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text='No matching answer'),
#             )
#             return

#         is_correct = user_answer == question.answer
#         user.save_answer(question, is_correct)
#         if is_correct:
#             response_message = '恭喜答對'
#         else:
#             response_message = '答錯了 :('

#         line_bot_api.reply_message(
#             event.reply_token,
#             [
#                 TextSendMessage(text=response_message),
#                 *get_message_for_next_question(user, event)
#             ]
#         )


# @line_webhook_handler.add(PostbackEvent)
# def handle_postback_answer(event):
#     user_id = event.source.user_id
#     user = get_quizzler_user(user_id)
#     data = dict(urlparse.parse_qsl(event.postback.data))
#     if data.get(ACTION) == SELECT_TICKET:
#         if user is not None:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text='無效：您已經註冊過了')
#             )
#             return
#         store.set(f'{user_id}.ticket', data.get('ticket'))
#         store.set(f'{user_id}.serial', False)
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text='請輸入您的 KKTIX 報名序號')
#         )
