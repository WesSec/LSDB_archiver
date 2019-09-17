import argparse
import configparser
import os

parser = argparse.ArgumentParser()


def loadargs():
    parser.add_argument("-i", "--ID", help="Enter a set ID to download")
    parser.add_argument("-l", "--list",
                        help="Location of a list (txt, every ID on a new row) with setlists to download")
    parser.add_argument("-o", "--output", help="Download location eg: /home/user/livesets (note, do not add a slash at "
                                               "the end default == project folder")
    args = parser.parse_args()
    return args


prog_path = os.path.dirname(os.path.abspath(__file__))


# Import the config file
def Load_config():
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(prog_path + "/config.ini")
    return config
