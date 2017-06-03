import os
import sys

from django.core.management import execute_from_command_line


if __name__ == '__main__':
    # Make sure the project root is discoverable.
    sys.path = [
        os.path.abspath(os.path.join(__file__, '..', '..')),
    ] + sys.path

    # Make sure dotenv is loaded.
    from quizzler import env    # noqa

    execute_from_command_line(sys.argv)
