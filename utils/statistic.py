from decimal import Decimal

from peewee import fn

from constants import ProfileResultStatusChoice
from models import *


class StatisticUtil:

    @staticmethod
    def game(profile: Profile, game: Game):
        query = ProfileResult.select().join(GameResult).where(
            ProfileResult.profile == profile,
        )
        wins = query.where(GameResult.game == game, ProfileResult.status == ProfileResultStatusChoice.WIN.value)
        draws = query.where(GameResult.game == game, ProfileResult.status == ProfileResultStatusChoice.DRAW.value)
        defeats = query.where(GameResult.game == game, ProfileResult.status == ProfileResultStatusChoice.DEFEAT.value)
        total = wins.count() + draws.count() + defeats.count()
        wr = round(Decimal(wins.count() / total * 100), 1) if total != 0 else 0
        text = (
            f'Игрок — @{profile.user.username}\n\n'
            f'Статистика по игре:\n'
            f'    Название — {game.name}\n'
            f'    Сыграно — {total}\n'
            f'    Побед — {wins.count()}\n'
            f'    Ничьих — {draws.count()}\n'
            f'    Поражений — {defeats.count()}\n'
            f'    Вин рейт — {wr}%'
            if game is not None
            else 'Нет подходящей для отображения статистики игры'
        )
        text += (
            '\n\nСтатистика по ролям:\n'
            '    - ' + '    - '.join(
                f'{i.name}\n'
                f'          Побед — {wins.where(ProfileResult.role == i).count()}\n'
                f'          Ничьих — {draws.where(ProfileResult.role == i).count()}\n'
                f'          Поражений — {defeats.where(ProfileResult.role == i).count()}\n'
                f'          Вин рейт — {round(Decimal(wins.where(ProfileResult.role == i).count() / total * 100), 1) if total != 0 else 0}%\n'
                for i in game.roles
            )
        ) if [i for i in game.roles] else ''
        text += (
            f'\nСтатистика по счёту:\n'
            f'    Лучший — {query.select(fn.MAX(ProfileResult.score)).scalar()}\n'
            f'    Средний — {query.select(fn.AVG(ProfileResult.score)).scalar()}\n'
            f'    Худший — {query.select(fn.MIN(ProfileResult.score)).scalar()}\n'
        ) if game.is_score else ''
        return text