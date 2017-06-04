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


def get_message_for_next_question(user, event):
    question = user.get_next_question()
    im.set_current_question(
        question=question,
        im_type='line',
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
            return get_message_for_next_question(user, self.event)
        else:
            return TextSendMessage(text=f'請輸入 email 以進行註冊：')

    def handle_select_answer(self):
        try:
            reply = parse('您選擇了：{answer}', self.message)['answer']
            current_question = im.get_current_question(
                im_type='line',
                im_id=self.user_id
            )
            is_correct = current_question.answer == reply
            self.user.save_answer(current_question, is_correct)
            score = self.user.get_current_score()
            if current_question.answer == reply:
                response = TextSendMessage(text=f'答對對啦～目前 {score} 分')
            else:
                response = TextSendMessage(
                    text=f'答錯錯嗚嗚嗚再接再厲！！目前 {score} 分'
                )
            return [
                response,
                *get_message_for_next_question(self.user, self.event)
            ]
        except im.CurrentQuestionDoesNotExist:
            return TextSendMessage('有人叫你回答嗎= =')

    def handle_message(self):
        if im.is_registration_session_active(
            im_type='line',
            im_id=self.user_id
        ):
            return self.handle_email_registration()
        elif self.message == '註冊' and self.user is None:
            return self.handle_begin_registration()
        elif self.message.startswith('您選擇了：'):
            return self.handle_select_answer()

    def handle_postback(self):
        if im.is_registration_session_active(
            im_type='line',
            im_id=self.user_id
        ):
            return self.handle_select_identity()
