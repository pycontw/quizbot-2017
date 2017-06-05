import os
import random
from parse import parse
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
    ConfirmTemplate,
)

from quizzler import users
from quizzler import questions
from quizzler import im
from quizzler import registrations


NICKNAME = 'Nickname (shown on ID card) / 暱稱 (顯示於識別證)'
SERIAL = '報名序號'
REGISTER = 'R'
MENU = 'M'

ROOT_URL = os.environ.get('ROOT_URL')


def generate_message_for_question(question):
    choices = [question.answer, *question.wrong_choices]
    random.shuffle(choices)
    choices = [*filter(lambda s: '皆' not in s, choices),
               *filter(lambda s: '皆' in s, choices)]

    if len(choices) > 4 or any(len(s) > 20 for s in choices):
        template = CarouselTemplate(
            columns=[CarouselColumn(
                title=f'選項 {option}',
                text=choice[:60],
                actions=[MessageTemplateAction(
                    label='選擇',
                    text=f'答案：{choice}')]
            ) for option, choice in zip('ABCDE', choices) if choice != '']
        )
        return [
            TextSendMessage(text=f'Q: {question.message}'),
            TemplateSendMessage(alt_text='Select answer', template=template)
        ]
    else:
        template = ButtonsTemplate(
            title='請作答：',
            text=f'Q: {question.message}',
            actions=[
                MessageTemplateAction(label=choice, text=f'答案：{choice}')
                for choice in choices if choice != ''
            ]
        )
        return [
            TemplateSendMessage(alt_text='Select answer', template=template)
        ]


def make_registered_user_menu():
    return [
        PostbackTemplateAction(label='開始遊戲', data=f'{MENU}:start'),
        PostbackTemplateAction(label='查看目前得分', data=f'{MENU}:score'),
        URITemplateAction(label='排行榜', uri=f'{ROOT_URL}/leaderboard'),
        PostbackTemplateAction(label='離開', data=f'{MENU}:leave')
    ]


def make_unregistered_user_menu():
    return [
        PostbackTemplateAction(label='開始註冊', data=f'{MENU}:register'),
        URITemplateAction(label='排行榜', uri=f'{ROOT_URL}/leaderboard'),
    ]


class Replier(object):
    def __init__(self, event):
        self.event = event
        self.user_id = event.source.user_id
        try:
            self.user = self.call(users.get_user)
        except users.UserDoesNotExist:
            self.user = None
        if event.type == 'message':
            self.message = event.message.text.strip()
        elif event.type == 'postback':
            self.postback = event.postback.data

    def call(self, function, **kwargs):
        return function(im_type='line', im_id=self.user_id, **kwargs)

    @property
    def current_question(self):
        if not hasattr(self, '_current_question'):
            try:
                self._current_question = self.call(im.get_current_question)
            except im.CurrentQuestionDoesNotExist:
                self._current_question = None
        return self._current_question

    def ask_next_question(self):
        question = self.user.get_next_question()
        self.call(im.set_current_question, question=question)
        return generate_message_for_question(question)

    def handle_begin_registration(self):
        self.call(im.activate_registration_session)
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
                    title='你是下面其中一位嗎？',
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
            self.user = self.call(users.add_user_im, serial=kktix_id)
            self.call(im.complete_registration_session)
            return [
                TextSendMessage(text='註冊成功！開始玩吧～'),
                *self.ask_next_question()
            ]
        else:
            return TextSendMessage(text=f'請輸入 email 以進行註冊：')

    def handle_select_answer(self):
        if self.current_question is None:
            return TextSendMessage(text='目前沒有進行中的題目喔～'
                                        '請輸入或按下「玩遊戲」來開始答題！')
        reply = parse('答案：{answer}', self.message)['answer']
        is_correct = self.current_question.answer == reply
        self.user.save_answer(self.current_question, is_correct)
        score = self.user.get_current_score()
        if self.current_question.answer == reply:
            response = TextSendMessage(text=f'答對對啦～目前 {score} 分')
        else:
            response = TextSendMessage(
                text=f'答錯錯嗚嗚嗚再接再厲！！目前 {score} 分'
            )
        return [response, *self.ask_next_question()]

    def handle_start_game(self):
        if self.current_question is not None:
            return TextSendMessage(text='遊戲已經在進行中～')
        else:
            return self.ask_next_question()

    def handle_pause_game(self):
        self.call(im.set_current_question, question=None)
        return TextSendMessage(
            text='狀態已清除！按「玩遊戲」以繼續玩遊戲計分～'
        )

    def ask_for_registration(self):
        return TemplateSendMessage(
            alt_text='註冊之後就可以開始玩囉！',
            template=ConfirmTemplate(
                text='註冊之後就可以開始玩囉！',
                actions=[
                    MessageTemplateAction(label='開始註冊', text='開始註冊'),
                    PostbackTemplateAction(label='取消', data='NOREGISTER'),
                ]
            )
        )

    def handle_lookup_score(self):
        return TextSendMessage(
            text=f'你目前的分數是：{self.user.get_current_score()} 分'
        )

    def handle_message(self):
        if self.user is None:
            if self.call(im.is_registration_session_active):
                return self.handle_email_registration()
            elif self.message == '開始註冊' and self.user is None:
                return self.handle_begin_registration()
            else:
                return self.ask_for_registration()
        else:
            if self.message.startswith('答案：'):
                return self.handle_select_answer()
            elif self.message == '玩遊戲':
                return self.handle_start_game()
            elif self.message == '不玩了':
                return self.handle_pause_game()
            elif self.message == '查分數':
                return self.handle_lookup_score()

    def handle_postback(self):
        if self.call(im.is_registration_session_active):
            return self.handle_select_identity()
        elif self.postback == 'NOREGISTER':
            return TextSendMessage(text='等你喔 >/////<')
