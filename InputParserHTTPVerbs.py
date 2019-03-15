#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse


def __validate_input__(args, parser, argList):
    t = str(args.target[0])
    argList.append(("target", t))

    p = int(args.port[0])

    if (p < 0 or p > 65535):
        print("Port out of range\n")
        __usage__(parser)
    argList.append(("port", p))


def __usage__(parser):
    parser.print_help()
    exit(0)


def __extract_tuple__(values):
    for val in values:
        if (val[0] == "target"):
            target = val[1]

        if (val[0] == "port"):
            port = val[1]

    return (target, port)


def parse_input(sysArgv=None):
    argList = []
    """parse_input """
    parser = argparse.ArgumentParser(
        prog="HTTPVerbs", usage="%(prog)s [options]")
    parser.add_argument(
        "-t",
        "--target",
        nargs=1,
        default=['a'],
        help="ip address of the target webserver")
    parser.add_argument(
        "-p",
        "--port",
        nargs=1,
        default=[80],
        help="port of the target webserver",
        type=int)

    if (sysArgv is None):
        args = parser.parse_args()
    else:
        args = parser.parse_args(sysArgv)
    __validate_input__(args, parser, argList)

    return __extract_tuple__(argList)
