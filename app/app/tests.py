from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import CustomUser
from .models import Video, Comment, History, Interaction


# Create your tests here.


def create_video(title, description, video, user):
    return Video.objects.create(title=title, description=description, video=video, user=user)


def create_comment(comment, user, video):
    return Comment.objects.create(comment=comment, user=user, video=video)


def create_like(user, video, like):
    return Interaction.objects.create(user=user, video=video, interaction_type=like)


def create_history(user, video, date):
    return History.objects.create(user=user, video=video, date=date)


class HistoryTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.client = Client()

    def test_history_no_logged(self):  # test if user is not logged in
        response = self.client.get('/video/history/')
        self.assertEqual(response.status_code, 302)

    def test_history_logged(self):  # test if user is logged in
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/video/history/')
        self.assertEqual(response.status_code, 200)

    def test_history(self):  # test if history is sorted by date
        self.client.login(username='testuser', password='12345')
        video1 = create_video('test', 'test', 'https://www.youtube.com/watch?v=wSTYIyQxfPQ', self.user)
        video2 = create_video('test2', 'test2', 'https://www.youtube.com/watch?v=xAz_DzPUjrM', self.user)
        video3 = create_video('test3', 'test3', 'https://www.youtube.com/watch?v=DviID8Ni7Ns', self.user)

        history1 = create_history(self.user, video1, '2023-03-11 02:36:13')
        history2 = create_history(self.user, video2, '2023-03-12 02:36:13')
        history3 = create_history(self.user, video3, '2023-03-13 02:36:13')

        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['videos'], [history3, history2, history1])


class PopularTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.client = Client()

    def test_popular_order(self):
        video1 = create_video('test', 'test', 'https://www.youtube.com/watch?v=wSTYIyQxfPQ', self.user)
        video2 = create_video('test2', 'test2', 'https://www.youtube.com/watch?v=xAz_DzPUjrM', self.user)
        video3 = create_video('test3', 'test3', 'https://www.youtube.com/watch?v=DviID8Ni7Ns', self.user)

        create_like(self.user, video1, "LIKE")
        create_like(self.user, video2, "LIKE")
        create_like(self.user, video3, "DISLIKE")

        create_comment('test', self.user, video1)

        response = self.client.get(reverse('popular'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['popular_videos'],
                                 [{'date': 3, 'popularity': 111,'video': video1},
                                  {'date': 3, 'popularity': 110,'video': video2},
                                  {'date': 3, 'popularity': 95,'video': video3}])


