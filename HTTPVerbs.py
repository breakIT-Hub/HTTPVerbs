#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from requests.exceptions import ConnectionError

from InputParserHTTPVerbs import parse_input


def init_values(argList=None):
    if (argList is None):
        return parse_input()
    else:
        return parse_input(argList)


def get_headers():
    return {
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0) \
               AppleWebKit/537.36 (KHTML, like Gecko) Edge/12.0"
    }


def enumerate_verbs(socket):
    answers = []
    verbs = []
    url = get_base_url(socket)
    headers = get_headers()
    data = {'test': 'test'}
    answers.append(("GET", requests.get(url, headers=headers)))
    answers.append(("HEAD", requests.head(url, headers=headers)))
    answers.append(("POST", requests.post(url, headers=headers, data=data)))
    answers.append(("PUT", requests.put(url, headers=headers, data=data)))
    answers.append(("DELETE", requests.delete(url, headers=headers)))
    # answers.append(("CONNECT", requests.c(url, headers=headers)))
    # answers.append(("TRACE", requests.trace(url, headers=headers)))
    answers.append(("PATCH", requests.patch(url, headers=headers)))
    print("Server {server} accepts:".format(server=socket[0]))

    for answer in answers:
        code = answer[1].status_code
        if (code != 405 and code != 501):
            verbs.append(answer[0])
    print("{verbs}".format(verbs=verbs))


def get_base_url(socket):
    return "http://" + socket[0] + ':' + str(socket[1])


def parse_answer(response, socket):
    if (response.status_code == requests.codes.ok):
        print("Allow: {allow}".format(allow=response.headers.get('Allow')))
    else:
        enumerate_verbs(socket)


def get_options(socket):
    try:
        r = requests.options(get_base_url(socket), headers=get_headers())
        parse_answer(r, socket)
    except ConnectionError:
        print("Server {server} on port {port} not reachable".format(
            server=socket[0], port=socket[1]))
        exit(0)


def main():
    socket = init_values()
    get_options(socket)


if __name__ == "__main__":
    main()
