import os
import sys

from django.core.management import execute_from_command_line


if __name__ == '__main__':
    sys.path = [
        os.path.abspath(os.path.join(__file__, '..', '..')),
    ] + sys.path
    execute_from_command_line(sys.argv)
