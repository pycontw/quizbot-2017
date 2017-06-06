import random


class MessageGetterMeta(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, {
            key: property(
                (lambda ms: lambda x: random.choice(ms))(messages)
            )
            for key, messages in attrs.items() if key.isupper()
        })


class MessageGetter(metaclass=MessageGetterMeta):

    CORRECT = [
        '答對對啦～',
        '恭喜答對！！',
        '來賓掌聲鼓勵鼓勵～～',
        '答對了！加油加油！',
        '對得我嫑嫑的 >////< ',
        '幾罷昏～',
    ]

    WRONG = [
        '答錯了 QQ ',
        '答錯了，再接再厲！',
        '答錯錯嗚嗚嗚～',
        '哎呀，差一點～',
        '錯！',
        '答錯幫QQ',
    ]


_ = MessageGetter()
