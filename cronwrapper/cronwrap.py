#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of cronwrapper utility released under the MIT license.
# See the LICENSE file for more information.

from __future__ import print_function
from optparse import OptionParser
import subprocess
import sys
import time
import datetime
import random
import hashlib
import tempfile
import os
import fcntl


class Lock(object):

    __file_handle = None
    file_complete_path = None

    def __init__(self, name, temp_dir=None):
        filename = hashlib.md5(name).hexdigest()
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        self.file_complete_path = os.path.join(temp_dir, filename)

    def __get_file_handle(self):
        if self.__file_handle is None:
            self.__file_handle = open(self.file_complete_path, "w+")
        return self.__file_handle

    def acquire(self):
        operation = fcntl.LOCK_EX | fcntl.LOCK_NB
        try:
            fcntl.lockf(self.__get_file_handle(), operation)
            return True
        except IOError:
            pass
        return False

    def release(self):
        if self.__file_handle is not None:
            fcntl.lockf(self.__file_handle, fcntl.LOCK_UN)
            self.__file_handle.close()
            try:
                os.unlink(self.file_complete_path)
            except:
                pass
            self.__file_handle = None


def usage():
    print("cronwrap.py [OPTIONS] command_to_execute")


def total_seconds(td):
    # backport from python 2.7
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) \
        / 10**6


def make_parser():
    parser = OptionParser()
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="command timeout (in seconds); 0 means no timeout; "
                      "default: 3600", metavar="TIMEOUT", default=3600,
                      type=int)
    parser.add_option("-r", "--random-sleep", dest="random_sleep",
                      help="wait a random value of seconds between 0 and "
                      "RVALUE before executing command (default 0: no random "
                      "wait)",
                      metavar="RVALUE", type=int, default=0)
    parser.add_option("-l", "--lock",
                      action="store_true", dest="lock", default=False,
                      help="don't execute the command another time if still "
                      "running (default False)")
    parser.add_option("-e", "--load-env", dest="load_env", action="store_true",
                      help="load environnement file before executing command "
                      "(default: False)", default=False)
    parser.add_option("-f", "--load-env-file", dest="load_env_file",
                      help="set the environnement file to load if load-env "
                      "option is set (default: ~/.bashrc)",
                      default="~/.bashrc")
    parser.add_option("-s", "--shell", dest="shell", help="full path of the "
                      "shell to use (default /bin/sh)")
    return parser


def random_sleep(random_sleep):
    if random_sleep != 0:
        random_int = random.randint(0, random_sleep)
        time.sleep(random_int)


def execute_command(command, shell):
    kwargs = {"shell": True}
    if shell:
        kwargs['executable'] = shell
    process = subprocess.Popen(command, **kwargs)
    return process


def make_command(original_command, load_env, load_env_file):
    if load_env:
        command = "source %s >/dev/null 2>&1 ; %s" % (load_env_file,
                                                      original_command)
    else:
        command = original_command
    return command


def wait_for_completion_or_kill(process, timeout):
    return_code = None
    before = datetime.datetime.now()
    while total_seconds(datetime.datetime.now() - before) <= timeout:
        return_code = process.poll()
        if return_code is not None:
            # Process has terminated
            break
        time.sleep(0.1)
    if return_code is None:
        # timeout
        print("timeout => kill -9", file=sys.stderr)
        process.kill()


def main():

    # CLI parsing
    parser = make_parser()
    (options, args) = parser.parse_args()
    if len(args) == 0:
        usage()
        sys.exit(1)

    # Random sleep
    random_sleep(options.random_sleep)

    # Command generation
    original_command = " ".join(args)
    command = make_command(original_command, options.load_env,
                           options.load_env_file)

    # Lock management
    command_hash = hashlib.md5(command).hexdigest()
    lock = Lock(command_hash)
    if not lock.acquire():
        print("can't acquire lock for executing %s => can be a normal "
              "behaviour" % original_command)
        sys.exit(0)

    # Command execution
    process = execute_command(command, options.shell)
    if options.timeout == 0:
        process.wait()
    else:
        wait_for_completion_or_kill(process, options.timeout)

    # Lock release
    lock.release()


if __name__ == "__main__":
    main()
