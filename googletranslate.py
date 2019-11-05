#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get translate from Google Translate
author: 'XINZENG ZHANG'
Created on 2018-04-18 17:04:00
USAGE:
python3 googletranslate.py <target language code> <text to be translated>
python googletranslate.py zh-CN 'hello world!'
"""

import requests
import sys
import urllib.parse
import asyncio
from functools import partial


def get_url(tl, qry):
    url = 'https://{}/translate_a/single?client=gtx&sl=auto&tl={}&dt=at&dt=bd&dt=ex&' \
          'dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&q={}'.format(http_host, tl, qry)
    return url


def get_synonym(result, resp):
    if resp[1]:
        result += '\n=========\n'
        result += '0_0: Translations of {}\n'.format(query_string)
        for x in resp[1]:
            result += '# {}.\n'.format(x[0][0])
            for y in x[2]:
                result += '{}: {}\n'.format(y[0], ", ".join(y[1]))
    return result


def get_result(results, resp):
    for x in resp[0]:
        results += x[0] if x[0] else ''
    return results


def get_definitions(result, resp):
    result += '\n=========\n'
    result += '0_0: Definitions of {}\n'.format(query_string)
    for x in resp[12]:
        result += '# {}.\n'.format(x[0]) if x[0] else ''
        for y in x[1]:
            result += '  - {}\n'.format(y[0])
            result += '    * {}\n'.format(y[2]) if len(y) >= 3 else ''
    return result


def get_examples(result, resp):
    result += '\n=========\n'
    result += '0_0: Examples of {}\n'.format(query_string)
    for x in resp[13][0]:
        result += '  - {}\n'.format(x[0].replace("<b>", "").replace("</b>", ""))
    return result


def get_synonyms_en(result, resp):
    result += '\n=========\n'
    result += '0_0: Synonyms of {}\n'.format(query_string)
    for x in resp[11]:
        result += "{}.\n---\n".format(x[0])
        for y in x[1]:
            result += ", ".join(y[0]) + "\n"
        result += "\n******\n"
    return result


def get_resp(url_resp, proxy):
    proxies = {
        "http": "http://{}".format(proxy.strip() if proxy.strip() else '127.0.0.1:1080'),
        "https": "http://{}".format(proxy.strip() if proxy.strip() else '127.0.0.1:1080')
    }
    base_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    session = requests.Session()
    session.headers = base_headers
    resp = session.get(url_resp, proxies=proxies if proxy.strip() else None, timeout=3).json()
    return resp


async def get_translation():
    if len(query_string) > 5000:
        print('(╯‵□′)╯︵┻━┻: Maximum characters exceeded...')
        return
    result = ''
    parse_query = urllib.parse.quote_plus(query_string)
    url = get_url(target_language, parse_query)
    url_alt = get_url(alternative_language, parse_query)
    try:
        loop = asyncio.get_running_loop()
        resp = loop.run_in_executor(None, partial(get_resp, url, http_proxy))
        resp_alt = loop.run_in_executor(None, partial(get_resp, url_alt, http_proxy))
        [resp, resp_alt] = await asyncio.gather(resp, resp_alt)
        if resp[2] == target_language:
            result += '^_^: Translate {} To {}\n'.format(resp[2], alternative_language)
            result = get_result(result, resp_alt) + '\n'
            result = get_result(result, resp)
            result = get_synonym(result, resp_alt)
        else:
            result += '^_^: Translate {} To {}\n{}\n'.format(resp[2], target_language, query_string)
            result = get_result(result, resp)
            result = get_synonym(result, resp)
        if synonyms_en and len(resp) >= 12 and resp[11]:
            result = get_synonyms_en(result, resp)
        if definitions_en and len(resp) >= 13 and resp[12]:
            result = get_definitions(result, resp)
        if examples_en and len(resp) >= 14 and resp[13]:
            result = get_examples(result, resp)
        print(result.encode(result_code, 'ignore').decode(result_code))
    except requests.exceptions.ReadTimeout:
        print('╰（‵□′）╯: ReadTimeout...')
    except requests.exceptions.ProxyError:
        print('(╯‵□′)╯︵┻━┻: ProxyError...')
    except:
        print('Errrrrrrrrror')


if __name__ == "__main__":
    http_host = 'translate.googleapis.com'
    http_proxy = ''
    target_language = sys.argv[1]
    query_string = sys.argv[2]
    synonyms_en = False
    definitions_en = True
    examples_en = False
    result_code = 'gbk'
    alternative_language = 'en'
    asyncio.run(get_translation())
