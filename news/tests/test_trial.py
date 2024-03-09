# news/tests/test_trial.py
import unittest
from django.test import TestCase

from news.models import News


class TestNews(TestCase):
    # Все нужные переменные сохраняем в атрибуты класса.
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            # При создании объекта обращаемся к константам класса через cls.
            title=cls.TITLE,
            text=cls.TEXT,
        )

    @unittest.skip('Этот тест мы просто пропускаем')
    def test_successful_creation(self):
        news_count = News.objects.count()
        self.assertEqual(news_count, 1)

    @unittest.skip('Этот тест мы просто пропускаем')
    def test_title(self):
        # Чтобы проверить равенство с константой -
        # обращаемся к ней через self, а не через cls:
        self.assertEqual(self.news.title, self.TITLE)
