from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
import json


def get_test_data():
    with open('site_checker/fixtures/test_data.json', 'r') as file:
        return json.loads(file.read())


class BaseTestCase(TestCase):
    fixtures = ['site_checker/fixtures/database.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data = get_test_data()
        self.login_user = \
            User.objects.get(username=self.test_data['login_username'])
        self.client = Client()
        self.client.force_login(self.login_user)


class AddUrlToCheck(BaseTestCase):

    def test_add_correct_url_string(self):
        self.client.post(reverse('add_urls'), {
            'url_string': self.test_data['correct_url_string']
        })
        response = self.client.get(reverse('url_list'))
        self.assertContains(response,
                            self.test_data['first_correct_url'])
        self.assertContains(response,
                            self.test_data['second_correct_url'])

    def test_add_half_correct_url_string(self):
        self.client.post(reverse('add_urls'), {
            'url_string': self.test_data['half_correct_url_string']
        })
        response = self.client.get(reverse('url_list'))
        self.assertContains(response,
                            self.test_data['first_correct_url'])
        self.assertNotContains(response,
                               self.test_data['second_correct_url'])

    def test_add_empty_url_string(self):
        response = self.client.post(reverse('add_urls'), {
            'url_string': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_add_url_string_with_redundant_part(self):
        response = (
            self.client.post(reverse('add_urls'), {
                'url_string': 'url_string_with_redundant_part'
            }))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('url_list'))
        self.assertNotContains(response,
                               self.test_data['first_correct_url'])

    def test_add_incomplete_url_string(self):
        response = self.client.post(reverse('add_urls'), {
            'url_string': 'incomplete_url_string'
        })
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('url_list'))
        self.assertNotContains(response,
                               self.test_data['first_correct_url'])

    def test_add_wrong_url(self):
        response = (
            self.client.post(reverse('add_urls'), {
                'url_string': 'url_string_with_wrong_url'
            }))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('url_list'))
        self.assertNotContains(response,
                               self.test_data['wrong_url'])

    def test_add_wrong_status_code(self):
        response = (
            self.client.post(reverse('add_urls'), {
                'url_string': 'url_string_with_wrong_status_code'
            }))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('url_list'))
        self.assertNotContains(response,
                               self.test_data['first_correct_url'])


class CheckUrl(BaseTestCase):

    def test_check_url_with_right_data(self):
        self.client.post(reverse('add_urls'), {
            'url_string': self.test_data['correct_url_string']
        })
        self.client.post(reverse('start_checks'))
        response = self.client.get(reverse('url_list'))
        self.assertNotContains(response,
                               self.test_data['wrong_check_string'])

    def test_check_url_with_all_incorrect_data(self):
        self.client.post(
            reverse('add_urls'), {
                'url_string': self.test_data['incorrect_url_string']
            })
        self.client.post(reverse('start_checks'))
        response = self.client.get(reverse('url_list'))
        self.assertContains(response,
                            self.test_data['wrong_title_check'])
        self.assertContains(response,
                            self.test_data['wrong_http_check'])
        self.assertContains(response,
                            self.test_data['wrong_https_check'])
        self.assertContains(response,
                            self.test_data['wrong_text_check'])


class PrepareUrlForAdding(BaseTestCase):

    def test_prepare_correct_url_string(self):
        self.client.post(
            reverse('parse_urls'), {
                'url_string': self.test_data['correct_urls_for_prepare']
            })
        response = self.client.get(reverse('parse_urls_list'))
        self.assertContains(response,
                            self.test_data['prepared_line'])

    def test_prepare_correct_url_string_and_add_to_url_list(self):
        self.client.post(
            reverse('parse_urls'), {
                'url_string': self.test_data['correct_urls_for_prepare'],
                'checkbox': True
            })
        response = self.client.get(reverse('parse_urls_list'))
        self.assertContains(response,
                            self.test_data['prepared_line'])
        response = self.client.get(reverse('url_list'))
        self.assertContains(response,
                            self.test_data['first_correct_url'])
        self.assertContains(response,
                            self.test_data['second_correct_url'])

    def test_prepare_empty_url_string(self):
        response = self.client.post(reverse('parse_urls'),
                                    {'url_string': ''})
        self.assertEqual(response.status_code, 200)

    def test_prepare_wrong_url_string(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['wrong_url']
        })
        self.assertEqual(response.status_code, 200)

    def test_prepare_access_denied_url(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['access_denied_url']
        })
        self.assertEqual(response.status_code, 200)


class CheckTextOnPage(BaseTestCase):

    def test_check_correct_text_string_with_right_and_wrong_text(self):
        self.client.post(reverse('check_text'), {
            'url_string': self.test_data['string_with_texts']
        })
        response = self.client.get(reverse('check_text_list'))
        self.assertContains(response,
                            self.test_data['right_text_confirmation'])
        self.assertContains(response,
                            self.test_data['wrong_text_confirmation'])

    def test_check_empty_text_string(self):
        response = self.client.post(reverse('parse_urls'),
                                    {'url_string': ''})
        self.assertEqual(response.status_code, 200)

    def test_check_text_string_with_redundant_part(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['string_with_redundant_part']
        })
        self.assertEqual(response.status_code, 200)

    def test_check_incomplete_text_string(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['incomplete_text_string']
        })
        self.assertEqual(response.status_code, 200)

    def test_check_text_string_with_wrong_url(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['string_with_wrong_url']
        })
        self.assertEqual(response.status_code, 200)

    def test_check_text_string_with_unavailable_url(self):
        response = self.client.post(reverse('parse_urls'), {
            'url_string': self.test_data['string_with_unavailable_url']
        })
        self.assertEqual(response.status_code, 200)
