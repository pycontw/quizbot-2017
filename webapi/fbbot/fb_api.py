import copy
import random

import requests

from django.conf import settings

from quizzler import im, users


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


def post_facebook_message(fbid, recevied_message, q=None):
    """
    Process:

    查詢 id
    -> 第一次進入遊戲
    -> 詢問 mail, serial
    -> 綁定 fb or line id
    -> 開始遊戲
    -> 第二次進入遊戲
    -> 開始遊戲
    """
    if q is None:
        q = []
    else:
        q = q

    api = MessengerAPI(fbid)

    if recevied_message == "not_exist_" + str(fbid):
        data = [
            {
                "type": "postback",
                "title": "輸入信箱開始註冊",
                "payload": "register_user"
            },
            {
                "type": "postback",
                "title": "不玩了",
                "payload": "exit"
            },
        ]
        api.sed_template_message(
            title="開始註冊",
            image_url=TITLE_IMAGE_URL,
            subtitle="歡迎 PyConTW 2017 大會遊戲",
            data=data,
        )
        return 0

    if recevied_message == "right" + str(fbid):
        api.send_text_message("答對了 ^^ 加油加油！")
        return 0

    if recevied_message == "wrong" + str(fbid):
        api.send_text_message("答錯了 QQ 再接再厲！")
        return 0

    if recevied_message == "查分數":
        user = users.get_user(im_type='fb', im_id=str(fbid))
        score = user.get_current_score()
        api.send_text_message(f"你目前的分數：{score}")
        return 0

    if recevied_message == "exit":
        api.send_text_message("記得要再回來啊～～～～！")
        return 0

    if recevied_message == "register_user":
        im.activate_registration_session(im_type='fb', im_id=str(fbid))
        api.send_text_message("請輸入註冊在 kktix 電子序號(ex:1)")
        return 0

    if im.is_registration_session_active(im_type='fb', im_id=fbid):
        if recevied_message.isdigit():
            try:
                user.get_user(im_type='fb', im_id=str(fbid))
            except users.UserDoesNotExist:
                users.add_user_im(
                    ticket='speaker',
                    serial=str(recevied_message),
                    im_type='fb', im_id=str(fbid),
                )
                api.send_text_message('註冊成功可以開始玩囉！')
            else:
                api.send_text_message('已經註冊了')
            im.complete_registration_session(im_type='fb', im_id=str(fbid))
        else:
            api.send_text_message('不合法的 kktix 序號，請再次輸入')
        return 0

    if recevied_message == "clean":
        api.send_text_message('清除狀態，雄壯威武！')
        im.complete_registration_session(im_type='fb', im_id=str(fbid))
        return 0

    if recevied_message == "開始玩":
        choices = copy.copy(q.wrong_choices)
        choices.append(q.answer)
        random.shuffle(choices)

        data = [
            {
                "content_type": "text",
                "title": choice,
                "payload": choice,
            }
            for choice in choices
        ]
        api.send_text_message(
            q.message,
            quick_replies=data,
        )
        return 0

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
