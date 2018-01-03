import unittest

from udoco import feeds
from udoco.tests import factory as _factory


class TestAllGameFeed(unittest.TestCase):

    def test_all_games(self):
        for i in range(0, 10):
            _factory.GameFactory()
        request = unittest.mock.Mock(method='GET')

        view = feeds.AllGameFeed()
        response = view(request)

        self.assertIn(
            'X-WR-CALNAME:UDO Colorado Upcoming Events',
            response.content.decode('utf-8'))
        self.assertIn(
            'X-WR-TIMEZONE:America/Denver',
            response.content.decode('utf-8'))
        self.assertEqual(
            10,
            len([
                line for line in response.content.decode('utf-8').split('\r\n')
                if line == 'BEGIN:VEVENT']))


class TestLeagueGameFeed(unittest.TestCase):

    def test_league_games(self):
        league = _factory.LeagueFactory()
        for i in range(0, 10):
            _factory.GameFactory(league=league)
        for i in range(0, 10):
            _factory.GameFactory()
        request = unittest.mock.Mock(method='GET')

        view = feeds.LeagueGameFeed()
        response = view(request, league_id=league.id)

        self.assertIn(
            'X-WR-CALNAME:{} Upcoming events'.format(league.name),
            response.content.decode('utf-8'))
        self.assertEqual(
            10,
            len([
                line for line in response.content.decode('utf-8').split('\r\n')
                if line == 'BEGIN:VEVENT']))
