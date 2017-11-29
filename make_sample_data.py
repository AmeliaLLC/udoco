from datetime import datetime, timedelta
import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'udoco.settings'
django.setup()

from udoco.tests.factory import GameFactory, LeagueFactory


league = LeagueFactory(name='Demo league')
print('Created league with id ', league.id)

date = datetime.now() + timedelta(days=7)
for _ in range(0, 20):
    GameFactory(start=date, league=league)
