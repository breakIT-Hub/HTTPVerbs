#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
import unittest
from unittest import mock

import pytest
import requests
import responses

import HTTPVerbs
from HTTPVerbs import init_values


class TestHTTPVerbs(unittest.TestCase):
    """Tests for HTTVerbs. """

    # admin inputs target and port with valid values
    def test_input_parser_valid_values(self):
        args = ["-t", "1.2.3.4", "-p", "3456"]
        result = init_values(args)
        assert result == ("1.2.3.4", 3456)

    # admin inputs target and takes the default port 80
    def test_input_parser_valid_ip_default_port(self):
        args = ["-t", "1.2.3.4"]
        result = init_values(args)
        assert result == ("1.2.3.4", 80)

    # reads from stdout and compares with given content
    def get_invalid_output(self, func, args, content):
        cap = io.StringIO()
        sys.stdout = cap
        with pytest.raises(SystemExit):
            func(args)
        sys.stdout = sys.__stdout__
        assert content in cap.getvalue()
        assert "usage:" in cap.getvalue()

    # admin inputs invalid ip
    # def test_input_parser_invalid_ip(self):
    #    args = ["-t", "abc", "-p", "1234"]
    #    self.get_invalid_output(init_values, args, "ip address")

    # admin input invalid port
    def test_input_parser_invalid_port(self):
        args = ["-t", "1.2.3.4", "-p", "-1"]
        self.get_invalid_output(init_values, args, "Port")

    # admin doesn't know how to use the program.
    # he enters '-h' or '--help' to see the available options
    def test_show_help(self):
        args = ["-h"]
        self.get_invalid_output(init_values, args, "")

    # test get headers
    def test_get_headers(self):
        headers = HTTPVerbs.get_headers()
        assert "user-agent" in headers
        assert "Mozilla" in headers.get("user-agent")

    # test get_base_url
    def test_get_url_without_dir(self):
        assert HTTPVerbs.get_base_url(("127.0.0.1",
                                       111)) == "http://127.0.0.1:111"

    # admin wants to get all HTTP verbs his server is accepting.
    # He starts the program with the ip address and port of the webserver.
    # Webserver answers to OPTIONS with 200 OK and Allow: Header
    @responses.activate
    def test_parse_answer_server_providing_answer(self):
        responses.add(
            responses.OPTIONS,
            "http://127.0.0.1:111",
            headers={"Allow": "GET, UPDATE, PATCH, DELETE, OPTIONS"},
            status=200)
        cap = io.StringIO()
        sys.stdout = cap
        HTTPVerbs.get_options(('127.0.0.1', 111))
        sys.stdout = sys.__stdout__
        assert "Allow: GET, UPDATE, PATCH, DELETE, OPTIONS" in cap.getvalue()

    # admin wants to get all HTTP verbs his server is accepting.
    # He starts the program with the ip address and port of the webserver.
    # Webserver is not reachable.
    @responses.activate
    def test_parse_answer_server_unreachable(self):
        responses.add(
            responses.OPTIONS,
            "http://127.0.0.1:111",
            headers={"Allow": "GET, UPDATE, PATCH, DELETE, OPTIONS"},
            status=200)
        with pytest.raises(SystemExit):
            with pytest.raises(requests.exceptions.ConnectionError):
                HTTPVerbs.get_options(('127.0.0.1', 80))

    # admin wants to get all HTTP verbs his server is accepting.
    # He starts the program with the ip address and port of the webserver.
    # Webserver rejects OPTIONS. Need to enumerate Verbs.
    @responses.activate
    def test_options_http_server_with_answer_not_ok(self):
        responses.add(responses.OPTIONS, "http://127.0.0.1:111", status=405)
        responses.add(responses.GET, "http://127.0.0.1:111", status=200)
        responses.add(responses.HEAD, "http://127.0.0.1:111", status=200)
        responses.add(responses.POST, "http://127.0.0.1:111", status=200)
        responses.add(responses.PUT, "http://127.0.0.1:111", status=501)
        responses.add(responses.DELETE, "http://127.0.0.1:111", status=200)
        # responses.add(responses.CONNECT, "http://127.0.0.1:111", status=404)
        # responses.add(responses.TRACE, "http://127.0.0.1:111", status=404)
        responses.add(responses.PATCH, "http://127.0.0.1:111", status=405)
        cap = io.StringIO()
        sys.stdout = cap
        HTTPVerbs.get_options(('127.0.0.1', 111))
        sys.stdout = sys.__stdout__
        out = cap.getvalue()
        assert "OPTIONS" not in out
        assert "PUT" not in out
        # assert "CONNECT" not in out
        # assert "TRACE" not in out
        assert "PATCH" not in out
        assert "GET" in out
        assert "HEAD" in out
        assert "POST" in out
        assert "DELETE" in out
