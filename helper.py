import json
import os
import subprocess as sp
import sys

from constants import *


class CmdWrapper:
    def __init__(self, command: str):
        self.command = command

    def run(self) -> (bool, str):
        try:
            result = sp.run(self.command, shell=True, check=True, capture_output=True, env=os.environ)

            if result.returncode == 0:
                return True, result.stdout.decode('utf-8')
            else:
                print_red(f"Command '{self.command}' failed with return code {result.returncode}")
                print_yellow(f"Stdout: {result.stdout.decode('utf-8')}")
                print_red(f"Stderr: {result.stderr.decode('utf-8')}")
                return False, result.stdout.decode('utf-8')
        except sp.CalledProcessError as e:
            print_red(f"CalledProcessError: Command '{self.command}' failed with return code {e.returncode}")
            print_red(f"Error: {e}")
            return False, e
        except Exception as e:
            print_red("Unpected error while running command '{self.command}'")
            print_red(f"Error: {e}")
            return False, e

class Deserializer:
    def __init__(self, ndjson_str: str):
        self.ndjson_str = ndjson_str
        self.ndjson_obj = json.loads(ndjson_str)
        self.url = self.ndjson_obj['URL']
        
        for field in SCORE_FIELDS:
            setattr(self, field.lower(), self[field])

        for field in LATENCY_FIELDS:
            setattr(self, field.lower(), self[field])


    def __getitem__(self, key: str):
        key_lower = key.lower()
        obj_key_map = {x.lower(): x for x in self.ndjson_obj.keys()}
        if key_lower in obj_key_map:
            return self.ndjson_obj[obj_key_map[key_lower]]
        return None


    # If any score is outside the range [0,1] then the score is invalid
    def is_valid(self):
        try:
            for field in SCORE_FIELDS:
                value = getattr(self, field.lower())
                if not (0 <= value <= 1 or value == -1):
                    return False
                
            for field in LATENCY_FIELDS:
                value = getattr(self, field.lower())
                if not (0 <= value or value == -1):
                    return False
            
            return True
        except TypeError as e:
            print_red(f"Incorrect type for field '{field}'. Expected float, got '{type(value)}'")
            print_red(f"Error: {e}")
            return False
        except Exception as e:
            print_red(f"Unpected error while validating field '{field}'")
            print_red(f"Error: {e}")
            return False


def print_green(msg: str):
    print(f"{GREEN}{msg}{RESET}")

def print_red(msg: str):
    print(f"{RED}{msg}{RESET}")

def print_yellow(msg: str):
    print(f"{YELLOW}{msg}{RESET}")

def print_blue(msg: str):
    print(f"{BLUE}{msg}{RESET}")

def print_test_result(test_msg: str, result: bool, true_msg: str = "True", false_msg: str = "False"):
    if result:
        print_green(test_msg % true_msg)
    else:
        print_red(test_msg % false_msg)