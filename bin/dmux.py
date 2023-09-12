#!/usr/bin/env python
import argparse

main_parser = argparse.ArgumentParser(prog='dmux')
sub_parser = main_parser.add_subparsers(help='sub-command help')
parser_a = sub_parser.add_parser('run', help='run subcommand help')
parser_b = sub_parser.add_parser('logs', help='logs subcommand help')


def run():
    pass

def logs():
    pass

if __name__ == '__main__':
    pass