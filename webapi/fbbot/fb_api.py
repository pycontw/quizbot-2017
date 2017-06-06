import copy
import random
import re
import logging

import requests

from django.conf import settings
from collections import OrderedDict

from quizzler import im
from quizzler import users
from quizzler import registrations

from .messages import MessageGetter


logger = logging.getLogger(__name__)


FACEBOOK_API_ENDPOINT = 'https://graph.facebook.com/v2.6/me/messages'


class MessengerAPI:

    def __init__(self, fb_id):
        self.fb_id = fb_id

    def post_to_facebook(self, *, json):
        requests.post(
            FACEBOOK_API_ENDPOINT, json=json,
            params={'access_token': settings.FACEBOOK_ACCESS_TOKEN},
        )

    def send_text_message(self, content, *, quick_replies=None):
        data = {
            "recipient": {"id": self.fb_id},
            "message": {"text": content},
        }
        if quick_replies is not None:
            data['message']['quick_replies'] = quick_replies
        self.post_to_facebook(json=data)

    def send_template_message(self, title, image_url, subtitle, data):
        self.post_to_facebook(json={
            "recipient": {"id": self.fb_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": title,
                                "image_url": image_url,
                                "subtitle": subtitle,
                                "buttons": data
                            },
                        ],
                    },
                },
            },
        })


TITLE_IMAGE_URL = \
    "https://pbs.twimg.com/profile_images/851073823357059072/dyff_G3a.jpg"


def get_question(api, q):
    choices = copy.copy(q.wrong_choices)
    choices.append(q.answer)
    random.shuffle(choices)
    if '以上皆非' in choices:
        choices.remove('以上皆非')
        choices.append('以上皆非')
    elif '以上皆是' in choices:
        choices.remove('以上皆是')
        choices.append('以上皆是')
    mapping_list = '(A)', '(B)', '(C)', '(D)', '(E)', '(F)'
    api.send_text_message("題目: {}".format(q.message))
    question_list = [ "{}: {}".format(mapping_list[i], choices[i]) for i in range(0, len(choices))]
    api.send_text_message('\n'.join(question_list))
    
    data = [
        {
            "content_type": "text",
            "title": choice,
            "payload": choice,
        }
        for choice in choices
    ]
    api.send_text_message(
        "答案是？",#q.message,
        quick_replies=data,
    )
    return 0


def post_facebook_message(fbid, recevied_message, q=None):
    if q is None:
        q = []
    else:
        q = q

    api = MessengerAPI(fbid)
    msg = MessageGetter(types=recevied_message.split('_')[0])
    logger.debug('接收字串：{}, 隨機回答：{}'.format(recevied_message, msg.randon_choice()))


    if recevied_message == "rm":
        api.send_text_message(msg.randon_choice())
        data = [
            {
                "type": "postback",
                "title": "確定刪除",
                "payload": "rmsure"
            },
            {
                "type": "postback",
                "title": "不要，我想留下來",
                "payload": "stay"
            }
        ]
        api.send_template_message(
            title="最後的抉擇",
            image_url=TITLE_IMAGE_URL,
            subtitle="請選擇",
            data=data,
        )
        return 0
        
    if recevied_message == "rmsure":
        api.send_text_message(msg.randon_choice())
        users.remove_user_im(im_type='fb', im_id=str(fbid))
        return 0

    if recevied_message == "stay":
        api.send_text_message('決定繼續挑戰！')
        data = [
            {
                "type": "postback",
                "title": "開始玩",
                "payload": "開始玩"
            },
            {
                "type": "postback",
                "title": "不玩了",
                "payload": "exit"
            }
        ]
        api.send_template_message(
            title="開始遊戲",
            image_url=TITLE_IMAGE_URL,
            subtitle="請選擇",
            data=data,
        )
        return 0

    if recevied_message == 'leaderboard':
        api.send_text_message('{}'.format(users.generate_leaders()))
        return 0

    if recevied_message == "clean":
        api.send_text_message('恭喜啊，清除狀態了！')
        im.complete_registration_session(im_type='fb', im_id=str(fbid))
        return 0
        
    if recevied_message == "error" + str(fbid):
        api.send_text_message('好像有錯誤啊 QQ，聯絡一下萬能 TP 主席大大吧！')
        return 0

    if recevied_message == "notexist_" + str(fbid):
        data = [
            {
                "type": "postback",
                "title": "輸入信箱開始註冊",
                "payload": "registeruser"
            },
            {
                "type": "postback",
                "title": "不玩了",
                "payload": "exit"
            },
        ]
        api.send_template_message(
            title="開始註冊",
            image_url=TITLE_IMAGE_URL,
            subtitle="歡迎 PyConTW 2017 大會猜謎機器人遊戲",
            data=data,
        )
        return 0

    if recevied_message == "exit":
        im.set_current_question(question=None, im_type='fb', im_id=str(fbid))
        api.send_text_message(msg.randon_choice())
        return 0

    if recevied_message == "right_" + str(fbid):
        api.send_text_message(msg.randon_choice())
        return get_question(api=api, q=q)
        
    if recevied_message == "wrong_" + str(fbid):
        api.send_text_message(msg.randon_choice())
        return get_question(api=api, q=q)

    if str(recevied_message).split('*')[0] == "start_regist" + str(fbid):
        users.add_user_im(
            serial=str(recevied_message).split('*')[1],
            im_type='fb', im_id=str(fbid),
        )
        api.send_text_message('註冊成功!!!可以開始玩囉！')
        
        data = [
            {
                "type": "postback",
                "title": "開始玩",
                "payload": "開始玩"
            },
            {
                "type": "postback",
                "title": "不玩了",
                "payload": "exit"
            }
        ]
        api.send_template_message(
            title="開始遊戲",
            image_url=TITLE_IMAGE_URL,
            subtitle="請選擇",
            data=data,
        )
        return 0

    if recevied_message == "registeruser":
        im.activate_registration_session(im_type='fb', im_id=str(fbid))
        api.send_text_message("請輸入註冊在 kktix 信箱")
        return 0

    if im.is_registration_session_active(im_type='fb', im_id=str(fbid)):
        match = re.match(
            '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
            str(recevied_message)
        )
        if match == None:
            api.send_text_message('不合法的信箱，請重新輸入')
        else:
            im.complete_registration_session(im_type='fb', im_id=str(fbid))
            # 確定是否有綁定 im_id
            try:
                users.get_user(im_type='fb', im_id=str(fbid))
            except users.UserDoesNotExist:
                user_infos = registrations.get_registrations(email=str(recevied_message))
                api.send_text_message('查詢中，請等待...')
                if user_infos == []:
                    api.send_text_message('查詢不到 {} 這個郵件, QQ 了，好想和你玩喔！'.format(recevied_message))
                else:
                    data = [
                        {
                            "type": "postback",
                            "title": '#'+user_info['報名序號']+', '+user_info['聯絡人 姓名'],
                            "payload": str('@@_'+user_info.uid)
                        }
                        for user_info in user_infos
                    ]
                    data.append(
                        {
                            "type": "postback",
                            "title": '取消',
                            "payload": 'exit'
                        }
                    )
                    api.send_template_message(
                        title="請選擇",
                        image_url=TITLE_IMAGE_URL,
                        subtitle="選擇綁定資料",
                        data=data,
                    )
            else:
                api.send_text_message('這個 FB 帳號已經綁定了喔！直接玩吧 yaya！')
        return 0

    if recevied_message == "查分數":
        user = users.get_user(im_type='fb', im_id=str(fbid))
        score = user.get_current_score()
        api.send_text_message(f"你目前的分數：{score}")
        return 0

    if recevied_message == "開始玩":
        return get_question(api=api, q=q)


    #瞎聊
    msg = MessageGetter(types='info')
    api.send_text_message(msg.randon_choice())
