import argparse
import datetime
import itertools
import os
import subprocess
import sys
import time

import psutil

def search_processes(proc_name):
    return [p for p in psutil.process_iter() if proc_name in p.name()]

def dump_all(proc_name, time_limit):
    procs = search_processes(proc_name)
    if not procs:
        sys.exit('No processes found matching query "%s"' % proc_name)

    now = datetime.datetime.now().replace(microsecond=0)
    dir_name = '_'.join([proc_name, now.isoformat()])
    os.mkdir(dir_name)
    os.chdir(dir_name)

    straces = []
    for proc in procs:
        output_fname = '%i.out' % proc.pid
        output_fd = open(output_fname, 'w')
        command = ['strace', '-p', str(proc.pid)]
        strace = subprocess.Popen(command,
                                  stdout=output_fd,
                                  stderr=subprocess.STDOUT,
                                  close_fds=True,
                                 )
        straces.append(strace)

    try:
        for i in itertools.count():
            if all(p.poll() is not None for p in straces):
                break
            elif time_limit and i > time_limit:
                break
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for strace in straces:
            strace.terminate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dump strace info for all processes matching query')
    parser.add_argument('proc_name', help='proceess name')
    parser.add_argument('-t', '--time_limit', type=int, default=60,
                        help='seconds to collect logs')
    parser.add_argument('-d', '--dest', help='directory to dump output')
    args = parser.parse_args()

    if args.dest is not None:
        os.chdir(args.dest)
    dump_all(args.proc_name, args.time_limit)
