#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import subprocess
import sys
import os
import time
import datetime
import random
import hashlib
import tempfile
from filelock import Timeout, FileLock
import psutil

DESCRIPTION = "A cron job wrapper to add some missing features " \
    "(locks, timeouts, random sleeps, env loading...)"


class DummyContextManager:

    def __enter__(self):
        pass

    def __exit__(self, *kwargs):
        pass


def make_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("COMMAND", help="command to execute (and its args)")
    parser.add_argument("--timeout", "-t",
                        help="command timeout (in seconds); "
                        "0 means no timeout; "
                        "default: 3600", default=3600, type=int)
    parser.add_argument("--random-sleep", "-r",
                        help="wait a random value of seconds between 0 and "
                        "RVALUE before executing command (default 0: "
                        "no random "
                        "wait)", type=int, default=0)
    parser.add_argument("--lock", "-l", action="store_true",
                        help="don't execute the command another time if still "
                        "running (default False)")
    parser.add_argument("--load-env", "-e", action="store_true",
                        help="load environnement file before executing "
                        "command (default: False)")
    parser.add_argument("--load-env-file", "-f",
                        help="set the environnement file to load if load-env "
                        "option is set (default: ~/.bashrc)",
                        default="~/.bashrc")
    parser.add_argument("--shell", "-s", help="full path of the "
                        "shell to use (default /bin/sh)")
    parser.add_argument("--nice", "-n", default=-99, type=int,
                        help="'nice' value (from -20 (most favorable "
                        "scheduling) to 19 (least favorable))")
    parser.add_argument("--ionice", "-i", default=0, type=int,
                        help="'ionice' class (1 for realtime, "
                        "2 for best-effort, "
                        "3 for idle)")
    parser.add_argument("--low", action="store_true",
                        help="short cut for '-i 3 -n 19' (minimum priority)")
    parser.add_argument("--log-capture-to", default=None,
                        help="if set, use log_proxy_wrapper to capture "
                        "stdout/stderr to the given log file (with rotation "
                        "and other features of log_proxy)")
    parser.add_argument("--wait-for-lock-timeout", "-w", default=1,
                        help="wait for lock timeout (default: 1 (second))",
                        type=int)
    parser.add_argument("--lock-timeout-behaviour", "-b",
                        default="print_stdout",
                        help="behaviour if lock timeout (print_stdout, "
                        "print_stderr or nothing)",
                        type=str)
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


def make_command(original_command, load_env, load_env_file, nice, ionice,
                 log_capture_to):
    command = ""
    if load_env:
        command = "source %s >/dev/null 2>&1 ; " % load_env_file
    if nice != -99:
        command += "nice -n %i " % nice
    if ionice != 0:
        command += "ionice -c %i " % ionice
    if log_capture_to is not None:
        command += "log_proxy_wrapper --stdout %s " \
            "--stderr STDOUT -- " % log_capture_to
    command += original_command
    return command


def wait_for_completion_or_kill(process, timeout):
    return_code = None
    before = datetime.datetime.now()
    while (datetime.datetime.now() - before).total_seconds() <= timeout:
        return_code = process.poll()
        if return_code is not None:
            # Process has terminated
            break
        time.sleep(1)
    if return_code is None:
        # timeout
        pid = process.pid
        print("timeout => kill -9 %i" % pid, file=sys.stderr)
        kill_process_and_children(pid)
        sys.exit(12)


def _kill_process_and_children(process):
    children = None
    try:
        children = process.children(recursive=False)
    except psutil.NoSuchProcess:
        pass
    try:
        process.kill()
    except psutil.NoSuchProcess:
        pass
    if children is not None:
        for child in children:
            _kill_process_and_children(child)


def kill_process_and_children(pid):
    """Kill recursively a complete tree of processes.

    Given a pid, this method recursively kills the complete tree (children and
    children of each child...) of this process.

    The SIGKILL signal is used.

    Args:
        pid (int): process PID to kill.

    """
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    _kill_process_and_children(process)


def main():

    # CLI parsing
    parser = make_parser()
    args, unknown = parser.parse_known_args()
    if args.low and args.nice != -99:
        parser.error("options low and nice are mutually exclusive")
        sys.exit(1)
    if args.low and args.ionice != 0:
        parser.error("options low and ionice are mutually exclusive")
        sys.exit(1)
    if args.low:
        args.nice = 19
        args.ionice = 3
    if args.lock_timeout_behaviour not in ('print_stdout', 'print_stderr',
                                           'nothing'):
        parser.error("lock-timeout-behaviour must be choosen between "
                     "print_stdout, print_stderr or nothing")
        sys.exit(1)

    # Random sleep
    random_sleep(args.random_sleep)

    # Command generation
    original_command = args.COMMAND + " " + " ".join(unknown)
    command = make_command(original_command, args.load_env,
                           args.load_env_file, args.nice, args.ionice,
                           args.log_capture_to)

    # Lock creation
    if args.lock:
        command_hash = hashlib.md5(command.encode('utf8')).hexdigest()
        lock_path = os.path.join(tempfile.gettempdir(),
                                 "cron-wrapper_%i_%s.lock" % (os.getuid(),
                                                              command_hash))
        lock = FileLock(lock_path, timeout=1)
    else:
        lock = DummyContextManager()

    try:
        with lock:
            # Command execution
            process = execute_command(command, args.shell)
            if args.timeout == 0:
                process.wait()
            else:
                wait_for_completion_or_kill(process, args.timeout)
    except Timeout:
        if args.lock_timeout_behaviour == "print_stdout":
            print("can't acquire lock for executing %s => can be a normal "
                  "behaviour" % original_command)
            sys.exit(0)
        elif args.lock_timeout_behaviour == "print_stderr":
            print("can't acquire lock for executing %s => can be a normal "
                  "behaviour" % original_command, file=sys.stderr)
            sys.exit(0)


if __name__ == "__main__":
    main()
