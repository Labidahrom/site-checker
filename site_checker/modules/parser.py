from __future__ import absolute_import
from bs4 import BeautifulSoup
import requests
import chardet
import re
from django.db import IntegrityError
from site_checker.models import (Url, Check, LastParse, TextCheckData,
                                 Notification)
from celery import shared_task
import time
import os
from dotenv import load_dotenv


load_dotenv()
USER_AGENT = os.getenv("USER_AGENT")


def validate_url_data_string(url_string):
    pattern = r'^(?!.*http(s)?://)[^|]+(\|\|[^|]+){4}$'
    return bool(re.match(pattern, url_string))


def validate_url_string(url_string):
    pattern = r'.*\..*'
    return bool(re.match(pattern, url_string))


def add_notification(notification):
    Notification.objects.create(notification=notification)


def strip_breaks(line):
    return line.strip('\r').strip('\n')


def strip_protocol(line):
    return line.replace("https://", "").replace("http://", "")


def make_request(url):
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = requests.get(url, allow_redirects=False, headers=headers)
        response.raise_for_status()
        coding_check = chardet.detect(response.content)
        encoding = coding_check['encoding']
        response.encoding = encoding
        return response
    except requests.RequestException as e:
        print(f"Failed to make a request to {url}. Error: {e}")


def prepare_page_content(response):
    if not response:
        return
    return BeautifulSoup(response.text, 'html.parser')


def extract_title(content):
    return content.title.string if content.title else None


def extract_h1(content):
    h1 = content.find('h1')
    return h1.text if h1 else None


def check_expected_text(content, text):
    return text in str(content)


def get_page_content(url_string):
    url = strip_breaks(url_string)
    if not validate_url_string(url):
        return
    http_response = make_request(f'http://{url}')
    https_response = make_request(f'https://{url}')
    if https_response:
        page_content = prepare_page_content(https_response)
    elif http_response:
        page_content = prepare_page_content(http_response)
    else:
        return
    return {
        'title': extract_title(page_content),
        'actual_response_by_http':
            http_response.status_code if http_response else None,
        'actual_response_by_https':
            https_response.status_code if https_response else None
    }, page_content


def check_url(url):
    page_data, page_content = get_page_content(url.name)
    page_data['has_expected_text'] = (
        check_expected_text(page_content, url.expected_text))
    return page_data


def format_url_data_to_string(url):
    page = get_page_content(url)
    if not page:
        return
    page_data, page_content = page
    return (f"||{page_data['title']}"
            f"||{page_data['actual_response_by_http']}"
            f"||{page_data['actual_response_by_https']}"
            f"||{extract_h1(page_content)}")


def make_check_details(url, check_data):
    status_field = ''
    if url.expected_title != check_data['title']:
        status_field += f'Title не совпадает: {check_data["title"]}. '
    if url.expected_response_by_http != check_data['actual_response_by_http']:
        status_field += (f'Http ответ не совпадает: '
                         f'{check_data["actual_response_by_http"]}. ')
    if (url.expected_response_by_https !=
            check_data['actual_response_by_https']):
        status_field += (f'Https ответ не совпадает: '
                         f'{check_data["actual_response_by_https"]}. ')
    if not check_data['has_expected_text']:
        status_field += 'Проверочный текст на странице не совпадает. '
    if not status_field:
        status_field = 'ok'
    return status_field


def prepare_url_data_string_for_db(url_string):
    url_data = url_string.split('||')
    return {
        'name': url_data[0],
        'expected_title': url_data[1],
        'expected_response_by_http': int(url_data[2]),
        'expected_response_by_https': int(url_data[3]),
        'expected_text': strip_breaks(url_data[4]),
    }


@shared_task
def add_urls_data_to_db(url_strings):
    url_list = url_strings.split('\n')
    for url_data_string in url_list:
        try:
            if not validate_url_data_string(url_data_string):
                print('object_not_valid')
                continue
            url_data = prepare_url_data_string_for_db(url_data_string)
            Url.objects.create(**url_data)
        except IntegrityError:
            print('object_didnt_created')
            continue
    add_notification(f'"{url_strings[:100]}" будут добавлены в базу данных')


@shared_task
def add_check_urls_data_to_db():
    current_time = time.ctime()
    add_notification(f'Проверка от {current_time} началась')
    urls_list = Url.objects.all()
    for url in urls_list:
        check_data = check_url(url)
        if not check_data:
            continue
        Check.objects.create(
            url_name=url,
            has_expected_title=check_data['title'] == url.expected_title,
            actual_response_by_http=check_data['actual_response_by_http'],
            actual_response_by_https=check_data['actual_response_by_https'],
            has_expected_text=check_data['has_expected_text']
        )
        status_string = make_check_details(url, check_data)

        if url.check_details != status_string:
            url_entry = Url.objects.get(id=url.id)
            url_entry.check_details = status_string
            url_entry.save()
    add_notification(f'Проверка от {current_time} закончилась')


def prepare_urls_data(url_strings):
    url_list = [strip_protocol(strip_breaks(url))
                for url in url_strings.split('\n')]
    parse_result = ''
    for url in url_list:
        parse_result += f'{url}{format_url_data_to_string(url)}\n'
    return parse_result


@shared_task
def add_prepared_urls_data_to_db(check_box, url_strings):
    if not url_strings:
        return
    add_notification(f'Подготовка {url_strings[:50]} началась')
    prepared_urls_data = prepare_urls_data(url_strings)
    if check_box:
        add_urls_data_to_db(prepared_urls_data)
    LastParse.objects.create(parse_data=prepared_urls_data)
    add_notification(f'Подготовка {url_strings[:50]} закончена')


def check_text_on_page(text_check_string):
    if '||' not in text_check_string:
        return ''
    url, text_to_find = strip_breaks(text_check_string).split('||')
    page = make_request(url)
    if page:
        has_text = text_to_find in page.text
        return f'{url}||{text_to_find}||{has_text}||{page.status_code}'
    else:
        return f'{url}||страница не найдена'


@shared_task
def add_text_check_data_to_db(text_check_strings):
    add_notification(
        f'Страницы "{text_check_strings[:50]}" добавлены в проверку')
    text_check_list = text_check_strings.split('\n')
    text_check_result = ''
    for string in text_check_list:
        text_check_string = check_text_on_page(string)
        text_check_result += (text_check_string + '\n')
    TextCheckData.objects.create(text_check_data=text_check_result)
    add_notification(f'Страницы "{text_check_strings[:50]}" проверены')
