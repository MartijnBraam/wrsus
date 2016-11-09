from arghandler import *

from wrsus import bootstrap


@subcmd
def init(parser, context, args):
    bootstrap.get_catalog()
    bootstrap.build_package_database()


if __name__ == '__main__':
    handler = ArgumentHandler()
    handler.run()
