import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, id_news_for_args, form_data
):
    url = reverse('news:detail', args=id_news_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        not_author_client, news, form_data
):
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text, form_data['text']
    assert comment.news, news
    assert comment.author, not_author_client


def test_user_cant_use_bad_words(
        not_author_client, id_news_for_args, form_data
):
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    url = reverse('news:detail', args=id_news_for_args)
    response = not_author_client.post(url, data=form_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:detail', args=(news.id,)) + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, id_comment_for_args
):
    delete_url = reverse('news:delete', args=id_comment_for_args)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, news, form_data):
    url = reverse('news:detail', args=(news.id,)) + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        news, comment, form_data, not_author_client
):
    edit_url = reverse('news:edit', args=(news.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
