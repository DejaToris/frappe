#!/usr/bin/env python3

import subprocess
import argparse
import re

WORKING_DIR = "/tmp/"
FFUF_KEYWORD = "FUZZ"
FFUF_PATH = "ffuf"

def main():
    parser = argparse.ArgumentParser(description="Pass arguments just like ffuf")
    # Define arguments
    parser.add_argument("-H", action="append", help="HTTP headers (can be repeated)")
    parser.add_argument("-D", help="Character dictionary in string form")
    parser.add_argument("-u", help="Target URL")
    parser.add_argument("-w", help="Path to dictionary")
    parser.add_argument("-X", help="HTTP method")
    parser.add_argument("-d", help="POST data")
    parser.add_argument("-fr", help="Filter by regex")

    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print(f"Unknown arguments: {unknown}")
        exit(1)

    # Access repeated arguments
    if args.H:
        print("Headers provided:")
        for header in args.H:
            print(header)

    # load dictionary to both a list and a file. the file will be passed to ffuf

    if args.D:
        dict = list(args.D)
        dict_path = WORKING_DIR + "dict.txt"
        with open(dict_path, "w") as dict_file:
            for char in args.D:
                dict_file.write(char + "\n")
    elif args.w:
        dict_path = args.w
        with open(dict_path, "r") as dict_file:
            lines = [line.strip() for line in dict_file]
    else:
        raise Exception("Please pass a dictionary in string or file path form!")

    secret = ""

    next_char = get_next_char_from_ffuf(args, dict_path, secret)
    while next_char :
        secret += next_char
        print(secret)
        next_char = get_next_char_from_ffuf(args, dict_path, secret)


def get_next_char_from_ffuf(args, dict_path, secret):
    new_args = generate_ffuf_args(args, dict_path, secret)
    ffuf_command = [FFUF_PATH] + new_args
    result = subprocess.run(ffuf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return parse_ffuf_result(result)

def generate_ffuf_args(args, dict_path, secret):
    new_args = []
    for arg_name, arg_value in vars(args).items():
        if arg_name == "w":
            new_args.append(f'-{arg_name}')
            new_args.append(dict_path)
        elif arg_name == "D":
            continue
        elif arg_name == "H":
            for header in arg_value:
                new_args.append(f'-{arg_name}')
                new_args.append(header)
        elif arg_value:
            new_args.append(f'-{arg_name}')
            if FFUF_KEYWORD in str(arg_value):
                new_element = str(arg_value).replace(FFUF_KEYWORD, f"{secret}{FFUF_KEYWORD}")
                new_args.append(new_element)
            else:
                new_args.append(arg_value)
    return new_args

def parse_ffuf_result(result):
    clean_result = result.stdout.decode('utf-8')
    if len(clean_result) > 0:
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]|\r', '', clean_result)[0]
    return None

if __name__ == '__main__':
    main()