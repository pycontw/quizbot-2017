import importlib
import functools
import logging
import pathlib
import re

import click

from quizzler import db


logger = logging.getLogger('migrations')


def init_system():
    logger.info('Init.')
    c = db.get_cursor()
    c.execute("""
        SELECT EXISTS(
            SELECT * FROM "information_schema"."tables"
            WHERE "table_name" = 'migration'
        )
    """)
    has_table, = c.fetchone()
    if not has_table:
        c.execute("""
            CREATE TABLE "migration" (
                "app" varchar(255) NOT NULL UNIQUE,
                "version" integer NOT NULL DEFAULT 0)
        """)
        c.execute("""
            INSERT INTO "migration" ("app", "version")
            VALUES ('quizzler', 0)
        """)
        logger.info('Migration table created.')


_migrations_dir_path = pathlib.Path(__file__).resolve().parent

_migration_filename_pattern = re.compile(r'^\d+(-\d+)?\.py$')


class MigrationNode:

    __slots__ = ['name', 'module', 'prev', 'next']

    def __init__(self, name, module):
        self.name = name
        self.module = module
        self.prev = None
        self.next = None

    def run_forward(self):
        logger.info(f'Apply {self.name}...')
        self.module.forward()


class MigrationRouteHead(MigrationNode):

    def __init__(self):
        super().__init__(None, None)

    def run_forward(self):
        pass


def load_migration_nodes():
    nodes = {None: MigrationRouteHead()}
    for path in _migrations_dir_path.iterdir():
        if not _migration_filename_pattern.match(path.name):
            continue
        module = importlib.import_module(f'quizzler.migrations.{path.stem}')
        nodes[path.stem] = MigrationNode(path.stem, module)

    # Fill linked-list info.
    for name, node in nodes.items():
        if name is None:
            continue
        prev_name = node.module.previous
        prev_node = nodes[prev_name]
        prev_node.next = node
        node.prev = prev_node

    return nodes


def record_target(f):

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        target_name = f(*args, **kwargs)
        c = db.get_cursor()
        c.execute("""
            UPDATE "migration"
            SET "version" = %(version)s
            WHERE "app" = 'quizzler'
        """, {'version': int(target_name)})

    return wrapped


RUN_ALL = object()


@record_target
def run_forward(current_name, target_name):
    nodes = load_migration_nodes()
    current_node = nodes[current_name]
    while current_node.name != target_name:
        if current_node.next is None and target_name is RUN_ALL:
            return current_node.name
        current_node = current_node.next
        current_node.run_forward()
    current_node.run_forward()
    return current_node.name


def get_current_name():
    c = db.get_cursor()
    c.execute("""
        SELECT "version" FROM "migration"
        WHERE "app" = 'quizzler'
        LIMIT 1
    """)
    version, = c.fetchone()
    if version < 1:
        return None
    return f'{version:04}'


@click.command()
@click.option('--target', default=RUN_ALL)
def main(target):
    current = get_current_name()
    run_forward(current, target)


if __name__ == '__main__':
    init_system()
    main()
