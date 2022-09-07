from enum import Enum


CANCEL_BUTTON = '⬅️ Отмена'
NEXT_BUTTON = '⏩ Далее'


class Choice(Enum):

    @classmethod
    def choices(cls):
        return [i.name for i in cls]

    @classmethod
    def values(cls):
        return [i.value for i in cls]


class GameScoreChoice(Choice):
    WIN = 1
    DRAW = 2
    DEFEAT = 3


class ProfileStatusChoice(Choice):
    PLAY = 1
    DONT = 0


class GameResultStatus(Choice):
    STARTED = 0
    FINISHED = 1
