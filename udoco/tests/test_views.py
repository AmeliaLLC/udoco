from importlib import import_module
import unittest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, QueryDict
from django.utils import timezone
import factory
import factory.fuzzy
import mock

from udoco import models
from udoco import views


class OfficialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Official
    username = factory.fuzzy.FuzzyText(prefix='user-')


class LeagueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.League


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Game
    title = factory.Sequence(lambda n: 'League %s' % n)
    start = factory.fuzzy.FuzzyDateTime(timezone.now())
    end = factory.fuzzy.FuzzyDateTime(timezone.now())

    association = factory.fuzzy.FuzzyInteger(0, 2)
    game_type = factory.fuzzy.FuzzyInteger(0, 1)

    creator = factory.SubFactory(OfficialFactory)
    league = factory.SubFactory(LeagueFactory)


class TestEventView(unittest.TestCase):

    def setUp(self):
        self.render_patcher = mock.patch('udoco.views.render')
        self.render = self.render_patcher.start()

    def tearDown(self):
        self.render_patcher.stop()

    def make_request(self, user=None, method='GET', ajax=False,
                     data=None, headers=None, secure=False,
                     with_session=False):
        """Returns an HTTP request for use in view tests."""
        if not user:
            user = AnonymousUser()
        if not data:
            data = {}
        if type(data) == str:
            querystring = data
        else:
            querystring = '&'.join([
                '{0}={1}'.format(k, v) for k, v in data.items()])

        request = HttpRequest()
        request.user = user
        request.META = {
            'SERVER_NAME': 'notarealserver',
            'SERVER_PORT': 80
        }

        # NOTE: rockstar (27 Apr 2014) - This is (obviously) a fake session
        # implementation. If you need something more than this implementation,
        # you should be using the Django Test Client in an integration test.
        mock_session = mock.Mock()
        mock_session.__contains__ = mock.Mock(return_value=True)
        mock_session.__getitem__ = mock.Mock(return_value=None)
        mock_session.get = mock.Mock(return_value=None)
        mock_session.__setitem__ = mock.Mock(return_value=None)
        request.session = mock_session

        if secure:
            # Monkeypatching is bad mmmkay?
            def is_secure(*args, **kwargs):
                return True
            request.is_secure = is_secure

        if method is 'GET':
            request.method = 'GET'
            request.GET = request.REQUEST = QueryDict(querystring)
        if method is 'POST':
            request.method = 'POST'
            request.POST = request.REQUEST = QueryDict(querystring)

        if headers:
            request.META.update(headers)

        if ajax:
            request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

        if with_session:
            engine = import_module(settings.SESSION_ENGINE)
            request.session = engine.SessionStore()

        return request

    def test_get_no_event(self):
        """If the event doesn't exist, an exception is raised."""
        request = self.make_request()

        view = views.EventView()

        self.assertRaises(models.Game.DoesNotExist, view.get, request, 1000000)

    def test_get(self):
        request = self.make_request()
        event = GameFactory()

        view = views.EventView()
        view.get(request, event.id)

        self.render.assert_called_once_with(
            request, 'udoco/event.html',
            {'event': event, 'can_schedule': False, 'form': None})

    def test_get_can_schedule(self):
        form = mock.Mock()
        request = self.make_request()
        official = OfficialFactory()
        request.user = official
        event = GameFactory()
        event.league.schedulers.add(official)
        event.league.save()

        view = views.EventView()
        view.form = mock.Mock()
        view.form.return_value = form
        view.get(request, event.id)

        self.render.assert_called_once_with(
            request, 'udoco/event.html',
            {'event': event, 'can_schedule': True, 'form': form})

    def test_get_cannot_schedule(self):
        form = mock.Mock()
        request = self.make_request()
        official = OfficialFactory()
        request.user = official
        event = GameFactory()

        view = views.EventView()
        view.form = mock.Mock()
        view.form.return_value = form
        view.get(request, event.id)

        self.render.assert_called_once_with(
            request, 'udoco/event.html',
            {'event': event, 'can_schedule': False, 'form': form})
