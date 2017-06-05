import random


class MessageGetter:

    correct_messages = [
        '答對對啦～',
        '恭喜答對！！',
        '來賓掌聲鼓勵鼓勵～～',
        '答對了！加油加油！',
        '對得我嫑嫑的 >////< ',
        '幾罷昏～',
    ]

    wrong_messages = [
        '答錯了 QQ ',
        '答錯了，再接再厲！',
        '答錯錯嗚嗚嗚～',
        '哎呀，差一點～',
        '錯！',
    ]

    @property
    def CORRECT(self):
        return random.choice(self.correct_messages)

    @property
    def WRONG(self):
        return random.choice(self.wrong_messages)


_ = MessageGetter()
