from bs4 import BeautifulSoup
import requests
import chardet

def make_request(url):
    try:
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        coding_check = chardet.detect(response.content)
        encoding = coding_check['encoding']
        response.encoding = encoding
        return response
    except requests.RequestException as e:
        print(f"Failed to make a request to {url}. Error: {e}")


def parse_page(response):
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


def get_page_content(url):
    print(url)
    url = url.strip('\r')
    http_response = make_request(f'http://{url}')
    print('http_response:', http_response)
    https_response = make_request(f'https://{url}')
    if https_response:
        page_content = parse_page(https_response)
    elif http_response:
        page_content = parse_page(http_response)
    else:
        return
    return {
        'title': extract_title(page_content),
        'actual_response_by_http': http_response.status_code if http_response else None,
        'actual_response_by_https': https_response.status_code if https_response else None
    }, page_content


def make_url_check(url):
    page_data, page_content = get_page_content(url.name)
    page_data['has_expected_text'] = check_expected_text(page_content, url.expected_text)
    return page_data


def parse_url(url):
    page_data, page_content = get_page_content(url)
    return f"||{page_data['title']}||{page_data['actual_response_by_http']}" \
           f"||{page_data['actual_response_by_https']}||{extract_h1(page_content)}"
