#!/bin/python3
from crawlers.wibly_crawler import WiblyCrawler
import sys
import argparse
import os
sys.setrecursionlimit(10000)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'gn_auto',
                    description = 'gn_auto is a tool to automatically download content that matches a set critera',
                    epilog = 'Copyright 2023 Slckly.com')
    parser.add_argument('--config', nargs='?', help="Path to configuration file or the name of the file located in the services directory.") 
    args = parser.parse_args()
    if args.config == None:
        parser.print_help()
        exit(1)
    crawler = WiblyCrawler()
    crawler.set_debug(True, None)
    if os.path.exists("services/"+args.config):
        crawler.load_config("services/"+args.config)
    elif os.path.exists(args.config):
        crawler.load_config(args.config)
    else:
        print("Invalid config file.")
    crawler.start()