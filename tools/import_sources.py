import csv
import pathlib

import yaml


def make_entry(row):
    return {
        'question': row[0],
        'answer': row[1],
        'wrong_choices': row[2:],
    }


def load_source(in_f, out_f):
    reader = csv.reader(in_f)
    entries = [make_entry(row) for row in reader]
    yaml.dump(entries, out_f, allow_unicode=True, default_flow_style=False)


def load_all():
    dirpath = pathlib.Path(__file__).parent
    for in_path in dirpath.glob('*.csv'):
        out_name = in_path.stem.split('-')[-1].strip()
        out_path = dirpath.joinpath(f'{out_name}.yml')
        with in_path.open() as in_f, out_path.open('w') as out_f:
            load_source(in_f, out_f)


if __name__ == '__main__':
    load_all()
