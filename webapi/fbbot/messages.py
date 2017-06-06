#!/usr/bin/python
# -*- coding: utf8 -*-
import random

from collections import namedtuple


class MessageGetter:

    msg_list = [
        ('info', '幹嘛'),
        ('info', '你是不是很想找我聊天？'),
        ('info', '和你說，我很忙滴'),
        ('info', '好好認真聽議程，議程組大大們就在後面喔'),
        ('info', '噓～你有聽到嗎？'),
        ('info', '和你說啦，PHP 才能做科學計算，老師在講你有沒有在聽 XD'),
        ('info', '現在是怎樣，玩我囉！'),
        ('info', '好說好說～～'),
        ('info', '有沒有覺得其實我很熱情'),
        ('info', '喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔喔，我好～興～奮～啊'),
        ('right', '答對了 ^^ 加油加油！'),
        ('right', '答對對啦～'),
        ('wrong', '答錯了 QQ 再接再厲！!'),
        ('wrong', '答錯錯嗚嗚嗚～'),
        ('rm', '你不要走～你不要走～但如果反悔了，重新註冊分數還在喔!!'),
        ('rm', '確定要走嗎？真的要走嗎！？不再考慮一下。\n好啦，想玩重新註冊分數還在喔！'),
        ('rmsure', '轉眼間，就刪除！'), 
        ('rmsure', '當啷，刪光了 QQ'),
        ('stay', '決定繼續挑戰！'),
        ('stay', '就知道你最有義氣，那再陪你摸兩把吧！'),
        ('exit', '真的要離開嗎 >///< 記得要再回來啊～～～～！'),
        ('exit', '主人，我會想你的喔 >////<')
    ]
    msgs = namedtuple('msg', ['type', 'content'])

    def __init__(self, types):
        self.types = types

    def randon_choice(self, m=None):
        if m is None:
            m = []
        else:
            m = m
        
        for msg in self.msg_list:
            if self.types in msg[0]:
                m.append(msg)
        
        if m != []:
            return self.msgs._make(random.choice(m)).content
        else:
            return "啊，我的詞庫沒有這個訊息 @@ 快點聯絡我的主人。"

    