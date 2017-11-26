from datetime import timedelta
import logging
import unittest

from django.test import TestCase
from django.utils import timezone
import factory
import factory.fuzzy
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from udoco import forms
from udoco import models
from udoco import views

logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)


class OfficialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Official
    display_name = factory.fuzzy.FuzzyText(prefix='Official ')
    username = factory.fuzzy.FuzzyText(prefix='user-')


class LeagueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.League
    name = factory.fuzzy.FuzzyText(prefix='league-')


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Game
    title = factory.fuzzy.FuzzyText(prefix='Event ')
    start = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=1),
        end_dt=timezone.now() + timedelta(days=10))
    end = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=11),
        end_dt=timezone.now() + timedelta(days=12))

    association = factory.fuzzy.FuzzyInteger(0, 2)
    game_type = factory.fuzzy.FuzzyInteger(0, 1)

    creator = factory.SubFactory(OfficialFactory)
    league = factory.SubFactory(LeagueFactory)


class RosterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Roster

    game = factory.SubFactory(GameFactory)


class ApplicationEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ApplicationEntry
    official = factory.SubFactory(OfficialFactory)
    event = factory.SubFactory(GameFactory)
    index = factory.fuzzy.FuzzyInteger(1)
    preference = factory.fuzzy.FuzzyChoice(
        tuple([x for x in range(0, 16)]))


class LoserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Loser
    derby_name = factory.fuzzy.FuzzyText()
    email_address = factory.fuzzy.FuzzyText(prefix='loser@')


class LoserApplicationEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LoserApplicationEntry
    official = factory.SubFactory(LoserFactory)
    event = factory.SubFactory(GameFactory)
    index = factory.fuzzy.FuzzyInteger(1)
    preference = factory.fuzzy.FuzzyChoice(
        tuple([x for x in range(0, 16)]))


class TestContactLeaguesView(unittest.TestCase):
    """Tests for udoco.views.ContactLeaguesView."""

    @unittest.mock.patch('udoco.views.render')
    def test_get(self, render):
        scheduler = OfficialFactory()
        league = LeagueFactory()
        scheduler.scheduling.add(league)
        user = OfficialFactory(is_staff=True)
        request = unittest.mock.Mock(user=user, method='GET')
        view = views.ContactLeaguesView.as_view()

        view(request)

        call = render.call_args[0]
        self.assertEqual(call[0], request)
        self.assertEqual(call[1], 'udoco/contact.html')
        self.assertIsInstance(
            call[2]['form'], forms.ContactOfficialsForm)
        self.assertIn(scheduler, call[2]['officials'])

    @unittest.mock.patch('udoco.views.messages')
    @unittest.mock.patch('udoco.views.mail')
    @unittest.mock.patch('udoco.views.redirect')
    def test_post(self, redirect, mail, messages):
        scheduler = OfficialFactory(email='abc@example.com')
        league = LeagueFactory()
        scheduler.scheduling.add(league)
        scheduler.save()
        user = OfficialFactory(is_staff=True)
        request = unittest.mock.Mock(user=user, method='POST')
        view = views.ContactLeaguesView.as_view()

        view(request)

        messages.add_message(
            request, messages.INFO, 'Your message has been sent')
        redirect.assert_called_once_with('contact_leagues')
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])


class TestMe(unittest.TestCase):
    """Tests for udoco.views.me."""

    def test_me_unauthorized(self):
        """When not logged in, there is no me."""
        factory = APIRequestFactory()
        request = factory.get('/api/me')

        response = views.me(request)

        self.assertEqual(401, response.status_code)

    def test_me(self):
        """Information about the user is retrieved."""
        user = OfficialFactory()
        factory = APIRequestFactory()
        request = factory.get('/api/me')
        force_authenticate(request, user=user)
        expected = {
            'id': user.id,
            'display_name': user.display_name,
            'email': user.email,
            'emergency_contact_name': user.emergency_contact_name,
            'emergency_contact_number': user.emergency_contact_number,
            'game_history': user.game_history,
            'avatar': user.avatar,
            'league': user.league,
            'league_affiliation': user.league_affiliation,
            'phone_number': user.phone_number
        }

        response = views.me(request)

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.data)

    def test_me_put(self):
        """Information about the user is updated."""
        user = OfficialFactory()
        factory = APIRequestFactory()
        data = {
            'display_name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'emergency_contact_name': 'Bob Mayhem',
            'emergency_contact_number': '18001234567',
            'game_history': 'https://example.com/history',
            'league_affiliation': 'Super league',
            'phone_number': '19001234567',
        }
        request = factory.put('/api/me', data, format='json')
        force_authenticate(request, user=user)

        response = views.me(request)

        self.assertEqual(200, response.status_code)
        for k in data.keys():
            self.assertEqual(data[k], response.data[k])


class TestEventViewSet(TestCase):
    """Tests for udoco.views.EventViewSet."""

    def setUp(self):
        super(TestEventViewSet, self).setUp()
        for i in range(0, 10):
            GameFactory()

    def test_list(self):
        client = APIClient()

        response = client.get('/api/events')

        self.assertEqual(200, response.status_code)
        self.assertEqual(10, len(response.data['results']))

    def test_create(self):
        league = LeagueFactory()
        user = OfficialFactory()
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)
        data = {
            'title': 'Quadruple header',
            'location': 'Anywhere, USA',
            'dateTime': 'Tue Oct 24 2020 00:00:00 GMT-0600 (MDT)'
        }

        response = client.post('/api/events', data, format='json')

        self.assertEqual(201, response.status_code)

    def test_create_no_schedule(self):
        """Users who can't schedule can't create events."""
        user = OfficialFactory()
        client = APIClient()
        client.force_authenticate(user)
        data = {
            'title': 'Quadruple header',
            'location': 'Anywhere, USA',
            'dateTime': 'Tue Oct 24 2020 00:00:00 GMT-0600 (MDT)'
        }

        response = client.post('/api/events', data, format='json')

        self.assertEqual(403, response.status_code)

    def test_update(self):
        game = GameFactory()
        user = OfficialFactory()
        user.scheduling.add(game.league)
        client = APIClient()
        client.force_authenticate(user)

        response = client.put(
            '/api/events/{}'.format(game.id),
            {'complete': True}, format='json')

        self.assertEqual(200, response.status_code)
        game = models.Game.objects.get(id=game.id)
        self.assertTrue(game.complete)

    @unittest.mock.patch('udoco.views.mail')
    def test_delete(self, mail):
        league = LeagueFactory()
        user = OfficialFactory(email='abc@example.com')
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = GameFactory(league=league)
        ApplicationEntryFactory(official=user, event=game)

        response = client.delete('/api/events/{}'.format(game.id))

        self.assertEqual(204, response.status_code)
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])

    @unittest.mock.patch('udoco.views.mail')
    def test_delete_completed_event(self, mail):
        league = LeagueFactory()
        user = OfficialFactory(email='abc@example.com')
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = GameFactory(league=league, complete=True)
        RosterFactory(hr=user, game=game)

        response = client.delete('/api/events/{}'.format(game.id))

        self.assertEqual(204, response.status_code)
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])

    @unittest.mock.patch('udoco.views.mail')
    def test_delete_disallowed(self, mail):
        """If the user's league doesn't own the event, it can't be deleted."""
        league = LeagueFactory()
        user = OfficialFactory()
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = GameFactory()

        response = client.delete('/api/events/{}'.format(game.id))

        self.assertEqual(403, response.status_code)


class TestLeagueScheduleViewSet(TestCase):
    """Tests for udoco.views.LeagueScheduleViewSet."""

    def test_list(self):
        for i in range(0, 10):
            GameFactory()

        league = LeagueFactory()
        user = OfficialFactory()
        user.scheduling.add(league)
        for i in range(0, 5):
            GameFactory(league=league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/league_schedule')

        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.json()))


class TestScheduleViewSet(TestCase):
    """Tests for udoco.views.ScheduleViewSet."""

    def test_list(self):
        user = OfficialFactory()
        RosterFactory(hr=user)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/schedule')

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_list_anonymous(self):
        RosterFactory()

        client = APIClient()

        response = client.get('/api/schedule')

        self.assertEqual(403, response.status_code)


class TestRosterViewSet(TestCase):
    """Tests for udoco.views.RosterViewSet."""

    def test_list(self):
        loser = LoserFactory()
        user = OfficialFactory()
        roster = RosterFactory(hr=user, ipr_x=loser)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/events/{}/rosters/'.format(roster.game.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        data = response.json()[0]
        self.assertEqual(user.id, data['hr'])
        self.assertEqual(loser.id, abs(data['ipr']))

    def test_list_anon(self):
        roster = RosterFactory()
        client = APIClient()

        response = client.get(
            '/api/events/{}/rosters/'.format(roster.game.id))

        self.assertEqual(403, response.status_code)

    def test_list_cant_schedule(self):
        loser = LoserFactory()
        user = OfficialFactory()
        roster = RosterFactory(hr=user, ipr_x=loser)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/events/{}/rosters/'.format(roster.game.id))

        self.assertEqual(403, response.status_code)

    def test_retrieve(self):
        user = OfficialFactory()
        roster = RosterFactory(hr=user)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/events/{}/rosters/{}/'.format(
                roster.game.id, roster.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])

    def test_create(self):
        game = GameFactory()
        user = OfficialFactory()
        loser = LoserFactory()
        user.scheduling.add(game.league)

        client = APIClient()
        client.force_authenticate(user)
        data = {'hr': user.id, 'ipr': 0 - loser.id}

        response = client.post(
            '/api/events/{}/rosters/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])
        self.assertEqual(0 - loser.id, response.json()['ipr'])

    def test_update(self):
        roster = RosterFactory()
        user = OfficialFactory()
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)
        data = {'hr': user.id, 'ipr': None}

        response = client.put(
            '/api/events/{}/rosters/{}/'.format(
                roster.game.id, roster.id),
            data, format='json')

        self.assertEqual(200, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])
        self.assertEqual(None, response.json()['ipr'])

    def test_destroy(self):
        user = OfficialFactory()
        roster = RosterFactory(hr=user)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/events/{}/rosters/{}/'.format(
                roster.game.id, roster.id))

        self.assertEqual(204, response.status_code)


class TestApplicationViewSet(TestCase):
    """Tests for udoco.views.ApplicationViewSet."""

    def test_list(self):
        entry = ApplicationEntryFactory()
        admin = entry.official
        admin.scheduling.add(entry.event.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/events/{}/applications/'.format(entry.event.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_list_not_logged_in(self):
        entry = ApplicationEntryFactory()

        client = APIClient()

        response = client.get(
            '/api/events/{}/applications/'.format(entry.event.id))

        self.assertEqual(404, response.status_code)

    def test_list_not_scheduler(self):
        entry = ApplicationEntryFactory()

        client = APIClient()
        client.force_authenticate(entry.official)

        response = client.get(
            '/api/events/{}/applications/'.format(entry.event.id))

        self.assertEqual(404, response.status_code)

    def test_create(self):
        user = OfficialFactory()
        game = GameFactory()

        client = APIClient()
        client.force_authenticate(user)
        data = ['1']

        response = client.post(
            '/api/events/{}/applications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual(1, game.applicants.count())

    def test_create_not_logged_in(self):
        game = GameFactory()

        client = APIClient()
        data = ['1']

        response = client.post(
            '/api/events/{}/applications/'.format(game.id),
            data, format='json')

        self.assertEqual(404, response.status_code)

    def test_create_cant_apply(self):
        entry = ApplicationEntryFactory()

        client = APIClient()
        client.force_authenticate(entry.official)
        data = ['1']

        response = client.post(
            '/api/events/{}/applications/'.format(entry.event.id),
            data, format='json')

        self.assertEqual(409, response.status_code)

    def test_delete(self):
        entry = ApplicationEntryFactory()
        user = entry.official

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/events/{}/applications/{}/'.format(
                entry.event.id, entry.id))

        self.assertEqual(204, response.status_code)
        game = models.Game.objects.get(pk=entry.event.id)
        self.assertEqual(0, game.applicants.count())

    def test_delete_not_logged_in(self):
        entry = ApplicationEntryFactory()

        client = APIClient()

        response = client.delete(
            '/api/events/{}/applications/{}/'.format(
                entry.event.id, entry.id))

        self.assertEqual(404, response.status_code)

    def test_delete_not_applied(self):
        entry = ApplicationEntryFactory()
        user = OfficialFactory()

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/events/{}/applications/{}/'.format(
                entry.event.id, entry.id))

        self.assertEqual(400, response.status_code)


class TestLoserApplicationViewSet(TestCase):

    def test_list(self):
        entry = LoserApplicationEntryFactory()
        admin = OfficialFactory()
        admin.scheduling.add(entry.event.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/events/{}/lapplications/'.format(entry.event.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_list_not_logged_in(self):
        entry = LoserApplicationEntryFactory()

        client = APIClient()

        response = client.get(
            '/api/events/{}/lapplications/'.format(entry.event.id))

        self.assertEqual(404, response.status_code)

    def test_list_not_admin(self):
        entry = LoserApplicationEntryFactory()
        user = OfficialFactory()

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/events/{}/lapplications/'.format(entry.event.id))

        self.assertEqual(404, response.status_code)

    def test_create(self):
        game = GameFactory()

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/events/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual(1, game.losers.count())

    def test_create_bad_data(self):
        game = GameFactory()

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'preferences': ['1']
        }

        response = client.post(
            '/api/events/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)

    def test_create_no_preferences(self):
        game = GameFactory()

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': []
        }

        response = client.post(
            '/api/events/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)

    def test_create_logged_in(self):
        game = GameFactory()

        client = APIClient()
        client.force_authenticate(OfficialFactory())
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/events/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(404, response.status_code)

    def test_create_date_in_the_past(self):
        game = GameFactory(
            start=timezone.now() - timedelta(days=1),
            end=timezone.now() - timedelta(days=10))

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/events/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)
