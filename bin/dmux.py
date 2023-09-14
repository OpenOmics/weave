#!/usr/bin/env python
import argparse

main_parser = argparse.ArgumentParser(prog='dmux')
sub_parser = main_parser.add_subparsers(help='sub-command help')
parser_run = sub_parser.add_parser('run', help='run subcommand help', required=True)
parser_logs = sub_parser.add_parser('logs', help='logs subcommand help', required=True)


def run():
    pass

def logs():
    pass

if __name__ == '__main__':
    args = main_parser.parse_args()
    import ipdb; ipdb.set_trace()
    pass