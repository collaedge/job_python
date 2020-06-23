# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

from sawtooth_job.job_client import JobClient
from sawtooth_job.job_exceptions import JobException


DISTRIBUTION_NAME = 'sawtooth-job'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def add_create_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'create',
        help='Creates a new job transaction',
        description='Creates a new job transaction with <workerId> <publisherId>'
        '<start_time> <end_time> <deadline> <base_rewards>.',
        parents=[parent_parser])

    parser.add_argument(
        'workerId',
        type=str,
        help='unique identifier for the worker')

    parser.add_argument(
        'publisherId',
        type=str,
        help='unique identifier for the publisher')

    parser.add_argument(
        'start_time',
        type=float,
        help='job start time')

    parser.add_argument(
        'end_time',
        type=float,
        help='job finish time')
    
    parser.add_argument(
        'deadline',
        type=float,
        help='expected job finish time')

    parser.add_argument(
        'base_rewards',
        type=float,
        help='given base rewards')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')


def add_list_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'list',
        help='Displays information for all xo games',
        description='Displays information for all xo games in state, showing '
        'the players, the game state, and the board for each game.',
        parents=[parent_parser])

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')


def add_show_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'show',
        help='Displays information about an xo game',
        description='Displays the xo game <name>, showing the players, '
        'the game state, and the board',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='identifier for the game')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    # parent_parser.add_argument(
    #     '-v', '--verbose',
    #     action='count',
    #     help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_create_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)

    return parser


def do_list(args):
    url = _get_url(args)
    # auth_user, auth_password = _get_auth_info(args)

    client = JobClient(base_url=url, keyfile=None)

    job_list = client.list()
    for job in job_list:
        for v in job.items():
            print('jobs'.v)
    

    # if game_list is not None:
    #     fmt = "%-15s %-15.15s %-15.15s %-9s %s"
    #     print(fmt % ('GAME', 'PLAYER 1', 'PLAYER 2', 'BOARD', 'STATE'))
    #     for game_data in game_list:

    #         name, board, game_state, player1, player2 = game_data

    #         print(fmt % (name, player1[:6], player2[:6], board, game_state))
    # else:
    #     raise JobException("Could not retrieve game listing.")


def do_show(args):
    jobId = args.jobId

    url = _get_url(args)
    # auth_user, auth_password = _get_auth_info(args)

    client = JobClient(base_url=url, keyfile=None)

    data = client.show(jobId)

    if data is not None:
        print('job'.data)
    else:
        raise JobException("Job not found: {}".format(jobId))


def do_create(args):
    print(args)
    workerId = args.workerId
    publisherId = args.publisherId
    start_time = args.start_time
    end_time = args.end_time
    deadline = args.deadline
    base_rewards = args.base_rewards

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    # auth_user, auth_password = _get_auth_info(args)

    client = JobClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create(
            workerId, publisherId,
            start_time, end_time, deadline,
            base_rewards, wait=args.wait,
            )
    else:
        response = client.create(
            workerId, publisherId,
            start_time, end_time, deadline,
            base_rewards)

    print("Response: {}".format(response))


# def do_take(args):
#     name = args.name
#     space = args.space

#     url = _get_url(args)
#     keyfile = _get_keyfile(args)
#     auth_user, auth_password = _get_auth_info(args)

#     client = XoClient(base_url=url, keyfile=keyfile)

#     if args.wait and args.wait > 0:
#         response = client.take(
#             name, space, wait=args.wait,
#             auth_user=auth_user,
#             auth_password=auth_password)
#     else:
#         response = client.take(
#             name, space,
#             auth_user=auth_user,
#             auth_password=auth_password)

#     print("Response: {}".format(response))


def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)


# def _get_auth_info(args):
#     auth_user = args.auth_user
#     auth_password = args.auth_password
#     if auth_user is not None and auth_password is None:
#         auth_password = getpass.getpass(prompt="Auth Password: ")

#     return auth_user, auth_password


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    # if args.verbose is None:
    #     verbose_level = 0
    # else:
    #     verbose_level = args.verbose

    # setup_loggers(verbose_level=verbose_level)

    if args.command == 'create':
        do_create(args)
    elif args.command == 'list':
        do_list(args)
    elif args.command == 'show':
        do_show(args)
    # elif args.command == 'take':
    #     do_take(args)
    else:
        raise JobException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except JobException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
