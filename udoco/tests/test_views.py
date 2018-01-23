from datetime import timedelta
import unittest

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from udoco import forms, models, views
from udoco.tests import factory as _factory


class TestCertbotView(unittest.TestCase):
    """Tests for udoco.views.certbot_view."""

    @unittest.mock.patch('udoco.views.settings')
    def test_response(self, settings):
        """A good public key results in the key being returned."""
        settings.CERTBOT_KEY = 'a.b'
        request = unittest.mock.Mock(method='GET')

        response = views.certbot_view(request, 'a')

        self.assertEqual(200, response.status_code)
        self.assertEqual(b'a.b', response.content)

    @unittest.mock.patch('udoco.views.settings')
    def test_bad_public_key(self, settings):
        """A 404 public/private key is returned."""
        settings.CERTBOT_KEY = 'a.b'
        request = unittest.mock.Mock(method='GET')

        response = views.certbot_view(request, 'c')

        self.assertEqual(404, response.status_code)


class TestContactLeaguesView(unittest.TestCase):
    """Tests for udoco.views.ContactLeaguesView."""

    @unittest.mock.patch('udoco.views.render')
    def test_get(self, render):
        scheduler = _factory.OfficialFactory()
        league = _factory.LeagueFactory()
        scheduler.scheduling.add(league)
        user = _factory.OfficialFactory(is_staff=True)
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
        scheduler = _factory.OfficialFactory(email='abc@example.com')
        league = _factory.LeagueFactory()
        scheduler.scheduling.add(league)
        scheduler.save()
        user = _factory.OfficialFactory(is_staff=True)
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
        user = _factory.OfficialFactory()
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
        user = _factory.OfficialFactory()
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


class TestFeedback(TestCase):
    """Tests for udoco.views.feedback."""

    def test_not_logged_in(self):
        """No anonymous feedback allowed."""
        factory = APIRequestFactory()
        request = factory.post('/api/feedback')

        response = views.feedback(request)

        self.assertEqual(401, response.status_code)

    @unittest.mock.patch('udoco.views.settings')
    @unittest.mock.patch('udoco.views.mail')
    def test_sends_mail(self, mail, settings):
        """Feedback sends mail."""
        settings.ADMINS = [('A Admin', 'admin@example.com')]
        user = _factory.OfficialFactory(email='abc@example.com')
        factory = APIRequestFactory()
        request = factory.post(
            '/api/feedback', {'message': 'ey yo'}, format='json')
        force_authenticate(request, user=user)

        response = views.feedback(request)

        self.assertEqual(200, response.status_code)
        call = mail.EmailMessage.call_args[0]
        self.assertEqual('Feedback for UDOCO', call[0].strip())
        self.assertIn('abc@example.com', call[1])
        self.assertEqual(['admin@example.com'], call[3])

    def test_no_malformed_data(self):
        """Malformed data results in a 400."""
        user = _factory.OfficialFactory()
        factory = APIRequestFactory()
        request = factory.post('/api/feedback', format='json')
        force_authenticate(request, user=user)

        response = views.feedback(request)

        self.assertEqual(400, response.status_code)

    def test_no_message_no_mail(self):
        """Missing the message key is also bad."""
        user = _factory.OfficialFactory()
        factory = APIRequestFactory()
        request = factory.post(
            '/api/feedback', {'_message': 'ey yo'}, format='json')
        force_authenticate(request, user=user)

        response = views.feedback(request)

        self.assertEqual(400, response.status_code)


class TestGameViewSet(TestCase):
    """Tests for udoco.views.GameViewSet."""

    def setUp(self):
        super(TestGameViewSet, self).setUp()
        for i in range(0, 10):
            _factory.GameFactory()

    def test_list(self):
        client = APIClient()

        response = client.get('/api/games')

        self.assertEqual(200, response.status_code)
        self.assertEqual(10, len(response.data['results']))

    def test_retrieve(self):
        game = _factory.GameFactory()
        client = APIClient()

        response = client.get('/api/games/{}'.format(game.id))

        self.assertEqual(200, response.status_code)

    def test_retrieve_not_found(self):
        client = APIClient()

        response = client.get('/api/games/83')

        self.assertEqual(404, response.status_code)

    def test_create(self):
        league = _factory.LeagueFactory()
        user = _factory.OfficialFactory()
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)
        data = {
            'title': 'Quadruple header',
            'location': 'Anywhere, USA',
            'start': '2020-10-24T00:00:00-06:10',
        }

        response = client.post('/api/games', data, format='json')

        self.assertEqual(201, response.status_code)
        json = response.json()
        self.assertEqual(data['title'], json['title'])
        self.assertEqual(data['location'], json['location'])
        self.assertEqual(data['start'], json['start'])
        game = models.Game.objects.get(pk=json['id'])
        self.assertEqual(2020, game.start.year)
        self.assertEqual(10, game.start.month)
        self.assertEqual(24, game.start.day)
        self.assertEqual(6, game.start.hour)
        self.assertEqual(10, game.start.minute)

    def test_create_no_schedule(self):
        """Users who can't schedule can't create games."""
        user = _factory.OfficialFactory()
        client = APIClient()
        client.force_authenticate(user)
        data = {
            'title': 'Quadruple header',
            'location': 'Anywhere, USA',
            'start': '2020-10-24T00:00:00-06:00',
        }

        response = client.post('/api/games', data, format='json')

        self.assertEqual(403, response.status_code)

    @unittest.mock.patch('udoco.views.mail')
    def test_partial_update_complete(self, mail):
        user = _factory.OfficialFactory(email='abc@example.com')
        roster = _factory.RosterFactory(hr=user)
        game = roster.game
        user.scheduling.add(game.league)
        client = APIClient()
        client.force_authenticate(user)

        response = client.patch(
            '/api/games/{}'.format(game.id),
            {'complete': True}, format='json')

        self.assertEqual(200, response.status_code)
        game = models.Game.objects.get(id=game.id)
        self.assertTrue(game.complete)
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])

    @unittest.mock.patch('udoco.views.mail')
    def test_partial_update(self, mail):
        user = _factory.OfficialFactory(email='abc@example.com')
        roster = _factory.RosterFactory(hr=user)
        game = roster.game
        user.scheduling.add(game.league)
        client = APIClient()
        client.force_authenticate(user)
        data = {
            'title': 'A new title',
            'location': 'A new location',
            'start': '2020-10-24T00:00:00-06:00',
        }

        response = client.patch(
            '/api/games/{}'.format(game.id),
            data, format='json')

        self.assertEqual(200, response.status_code)
        game = models.Game.objects.get(id=game.id)
        self.assertEqual('A new title', game.title)
        self.assertEqual('A new location', game.location)
        self.assertEqual(2020, game.start.year)
        self.assertEqual(10, game.start.month)
        self.assertEqual(24, game.start.day)
        self.assertFalse(game.complete)
        self.assertEqual(0, mail.EmailMessage.call_count)

    @unittest.mock.patch('udoco.views.mail')
    def test_delete(self, mail):
        league = _factory.LeagueFactory()
        user = _factory.OfficialFactory(email='abc@example.com')
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = _factory.GameFactory(league=league)
        _factory.ApplicationEntryFactory(official=user, game=game)

        response = client.delete('/api/games/{}'.format(game.id))

        self.assertEqual(204, response.status_code)
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])

    @unittest.mock.patch('udoco.views.mail')
    def test_delete_completed_game(self, mail):
        league = _factory.LeagueFactory()
        user = _factory.OfficialFactory(email='abc@example.com')
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = _factory.GameFactory(league=league, complete=True)
        _factory.RosterFactory(hr=user, game=game)

        response = client.delete('/api/games/{}'.format(game.id))

        self.assertEqual(204, response.status_code)
        call = mail.EmailMessage.call_args[1]
        self.assertIn('abc@example.com', call['bcc'])

    @unittest.mock.patch('udoco.views.mail')
    def test_delete_disallowed(self, mail):
        """If the user's league doesn't own the game, it can't be deleted."""
        league = _factory.LeagueFactory()
        user = _factory.OfficialFactory()
        user.scheduling.add(league)
        client = APIClient()
        client.force_authenticate(user)

        game = _factory.GameFactory()

        response = client.delete('/api/games/{}'.format(game.id))

        self.assertEqual(403, response.status_code)


class TestLeagueScheduleViewSet(TestCase):
    """Tests for udoco.views.LeagueScheduleViewSet."""

    def test_list(self):
        for i in range(0, 10):
            _factory.GameFactory()

        league = _factory.LeagueFactory()
        user = _factory.OfficialFactory()
        user.scheduling.add(league)
        for i in range(0, 5):
            _factory.GameFactory(league=league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/league_schedule')

        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.json()))

    def test_list_non_scheduler(self):
        user = _factory.OfficialFactory()

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/league_schedule')

        self.assertEqual(401, response.status_code)


class TestScheduleViewSet(TestCase):
    """Tests for udoco.views.ScheduleViewSet."""

    def test_list(self):
        user = _factory.OfficialFactory()
        _factory.RosterFactory(hr=user, game__complete=True)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/schedule')

        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(1, len(data))
        self.assertTrue(data[0]['complete'])

    def test_list_rostered_but_not_complete(self):
        user = _factory.OfficialFactory()
        _factory.RosterFactory(hr=user)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/schedule')

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))

    def test_list_anonymous(self):
        _factory.RosterFactory()

        client = APIClient()

        response = client.get('/api/schedule')

        self.assertEqual(403, response.status_code)

    def test_list_applied_but_not_complete(self):
        entry = _factory.ApplicationEntryFactory()
        user = entry.official

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/schedule')

        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(1, len(data))
        self.assertFalse(data[0]['complete'])
        self.assertTrue(data[0]['has_applied'])

    def test_list_applied_but_not_rostered(self):
        entry = _factory.ApplicationEntryFactory()
        entry.game.complete = True
        entry.game.save()
        user = entry.official

        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/schedule')

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()))


class TestRosterViewSet(TestCase):
    """Tests for udoco.views.RosterViewSet."""

    def test_list(self):
        loser = _factory.LoserFactory()
        user = _factory.OfficialFactory()
        roster = _factory.RosterFactory(hr=user, ipr_x=loser)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/games/{}/rosters/'.format(roster.game.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        data = response.json()[0]
        self.assertEqual(user.id, data['hr'])
        self.assertEqual(loser.id, abs(data['ipr']))

    def test_list_anon(self):
        roster = _factory.RosterFactory()
        client = APIClient()

        response = client.get(
            '/api/games/{}/rosters/'.format(roster.game.id))

        self.assertEqual(403, response.status_code)

    def test_list_cant_schedule(self):
        loser = _factory.LoserFactory()
        user = _factory.OfficialFactory()
        roster = _factory.RosterFactory(hr=user, ipr_x=loser)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/games/{}/rosters/'.format(roster.game.id))

        self.assertEqual(403, response.status_code)

    def test_retrieve(self):
        user = _factory.OfficialFactory()
        roster = _factory.RosterFactory(hr=user)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/games/{}/rosters/{}/'.format(
                roster.game.id, roster.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])

    def test_create(self):
        game = _factory.GameFactory()
        user = _factory.OfficialFactory()
        loser = _factory.LoserFactory()
        user.scheduling.add(game.league)

        client = APIClient()
        client.force_authenticate(user)
        data = {'hr': user.id, 'ipr': 0 - loser.id}

        response = client.post(
            '/api/games/{}/rosters/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])
        self.assertEqual(0 - loser.id, response.json()['ipr'])

    def test_update(self):
        roster = _factory.RosterFactory()
        user = _factory.OfficialFactory()
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)
        data = {'hr': user.id, 'ipr': None}

        response = client.put(
            '/api/games/{}/rosters/{}/'.format(
                roster.game.id, roster.id),
            data, format='json')

        self.assertEqual(200, response.status_code)
        self.assertEqual(user.id, response.json()['hr'])
        self.assertEqual(None, response.json()['ipr'])

    def test_destroy(self):
        user = _factory.OfficialFactory()
        roster = _factory.RosterFactory(hr=user)
        user.scheduling.add(roster.game.league)

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/games/{}/rosters/{}/'.format(
                roster.game.id, roster.id))

        self.assertEqual(204, response.status_code)


class TestApplicationViewSet(TestCase):
    """Tests for udoco.views.ApplicationViewSet."""

    def test_list(self):
        entry = _factory.ApplicationEntryFactory()
        admin = entry.official
        admin.scheduling.add(entry.game.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/games/{}/applications/'.format(entry.game.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_list_notes(self):
        entry = _factory.ApplicationEntryFactory()
        notes = _factory.ApplicationNotesFactory(
            official=entry.official, game=entry.game,
            content='Here is an note')
        admin = entry.official
        admin.scheduling.add(entry.game.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/games/{}/applications/'.format(entry.game.id))

        self.assertEqual(200, response.status_code)
        applications = response.json()
        self.assertEqual(1, len(applications))
        self.assertEqual(notes.content, applications[0]['notes'])

    def test_list_not_logged_in(self):
        entry = _factory.ApplicationEntryFactory()

        client = APIClient()

        response = client.get(
            '/api/games/{}/applications/'.format(entry.game.id))

        self.assertEqual(403, response.status_code)

    def test_list_not_scheduler(self):
        entry = _factory.ApplicationEntryFactory()

        client = APIClient()
        client.force_authenticate(entry.official)

        response = client.get(
            '/api/games/{}/applications/'.format(entry.game.id))

        self.assertEqual(403, response.status_code)

    def test_create(self):
        user = _factory.OfficialFactory()
        game = _factory.GameFactory()

        client = APIClient()
        client.force_authenticate(user)
        data = {'preferences': ['1']}

        response = client.post(
            '/api/games/{}/applications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual(1, game.applicants.count())

    def test_create_notes(self):
        user = _factory.OfficialFactory()
        game = _factory.GameFactory()

        client = APIClient()
        client.force_authenticate(user)
        data = {
            'notes': 'Here is a note',
            'preferences': ['1']}

        response = client.post(
            '/api/games/{}/applications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual(1, game.applicants.count())
        notes = models.ApplicationNotes.objects.get(
            official=user, game=game)
        self.assertEqual(notes.content, 'Here is a note')

    def test_create_not_logged_in(self):
        game = _factory.GameFactory()

        client = APIClient()
        data = {'preferences': ['1']}

        response = client.post(
            '/api/games/{}/applications/'.format(game.id),
            data, format='json')

        self.assertEqual(403, response.status_code)

    def test_create_cant_apply(self):
        entry = _factory.ApplicationEntryFactory()

        client = APIClient()
        client.force_authenticate(entry.official)
        data = {'preferences': ['1']}

        response = client.post(
            '/api/games/{}/applications/'.format(entry.game.id),
            data, format='json')

        self.assertEqual(409, response.status_code)

    def test_delete(self):
        entry = _factory.ApplicationEntryFactory()
        user = entry.official

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/games/{}/applications/0/'.format(entry.game.id))

        self.assertEqual(204, response.status_code)
        game = models.Game.objects.get(pk=entry.game.id)
        self.assertEqual(0, game.applicants.count())

    def test_delete_not_logged_in(self):
        entry = _factory.ApplicationEntryFactory()

        client = APIClient()

        response = client.delete(
            '/api/games/{}/applications/0/'.format(entry.game.id))

        self.assertEqual(403, response.status_code)

    def test_delete_not_applied(self):
        entry = _factory.ApplicationEntryFactory()
        user = _factory.OfficialFactory()

        client = APIClient()
        client.force_authenticate(user)

        response = client.delete(
            '/api/games/{}/applications/0/'.format(entry.game.id))

        self.assertEqual(400, response.status_code)


class TestLoserApplicationViewSet(TestCase):

    def test_list(self):
        entry = _factory.LoserApplicationEntryFactory()
        admin = _factory.OfficialFactory()
        admin.scheduling.add(entry.game.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/games/{}/lapplications/'.format(entry.game.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))

    def test_list_notes(self):
        entry = _factory.LoserApplicationEntryFactory()
        entry.official.notes = 'Here is a note'
        entry.official.save()
        admin = _factory.OfficialFactory()
        admin.scheduling.add(entry.game.league)

        client = APIClient()
        client.force_authenticate(admin)

        response = client.get(
            '/api/games/{}/lapplications/'.format(entry.game.id))

        self.assertEqual(200, response.status_code)
        lapplications = response.json()
        self.assertEqual(1, len(lapplications))
        self.assertEqual(entry.official.notes, lapplications[0]['notes'])

    def test_list_not_logged_in(self):
        entry = _factory.LoserApplicationEntryFactory()

        client = APIClient()

        response = client.get(
            '/api/games/{}/lapplications/'.format(entry.game.id))

        self.assertEqual(403, response.status_code)

    def test_list_not_admin(self):
        entry = _factory.LoserApplicationEntryFactory()
        user = _factory.OfficialFactory()

        client = APIClient()
        client.force_authenticate(user)

        response = client.get(
            '/api/games/{}/lapplications/'.format(entry.game.id))

        self.assertEqual(403, response.status_code)

    def test_create(self):
        game = _factory.GameFactory()

        client = APIClient()
        data = {
            'name': 'Maddy Mayhem',
            'email': 'maddy@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual(1, game.losers.count())

    def test_create_with_notes(self):
        game = _factory.GameFactory()

        client = APIClient()
        data = {
            'name': 'Maddy Mayhem',
            'email': 'maddy@example.com',
            'preferences': ['1'],
            'notes': 'Suh',
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(201, response.status_code)
        game = models.Game.objects.get(pk=game.id)
        self.assertEqual('Suh', game.losers.all()[0].notes)

    def test_create_bad_data(self):
        game = _factory.GameFactory()

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'preferences': ['1']
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)

    def test_create_no_preferences(self):
        game = _factory.GameFactory()

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': []
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)

    def test_create_logged_in(self):
        game = _factory.GameFactory()

        client = APIClient()
        client.force_authenticate(_factory.OfficialFactory())
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(403, response.status_code)

    def test_create_date_in_the_past(self):
        game = _factory.GameFactory(
            start=timezone.now() - timedelta(days=1))

        client = APIClient()
        data = {
            'name': 'Mike Mayhem',
            'email': 'abc@example.com',
            'preferences': ['1']
        }

        response = client.post(
            '/api/games/{}/lapplications/'.format(game.id),
            data, format='json')

        self.assertEqual(400, response.status_code)
