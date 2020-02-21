import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def str_from_file_name(file_name):
    file_path = os.path.join(__location__, file_name)
    with open(file_path, "r") as f:
        return f.read()
