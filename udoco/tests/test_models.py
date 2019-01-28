from django.test import TestCase

from udoco.tests import factory as _factory


class TestGame(TestCase):
    """Tests for udoco.models.Game."""

    def test_rostered(self):
        """A list of all rostered officials is returned, with no dupes."""
        user = _factory.OfficialFactory()
        roster1 = _factory.RosterFactory(hr=user)
        _factory.RosterFactory(game=roster1.game, hr=user)

        rostered = roster1.game.rostered

        self.assertEqual(1, len(rostered))
