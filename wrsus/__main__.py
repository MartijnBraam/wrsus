from arghandler import *

from wrsus import bootstrap
import wrsus.downloader as downloader


@subcmd('init', help='Create the initial update database')
def init(parser, context, args):
    bootstrap.get_catalog()
    bootstrap.build_package_database()


@subcmd('download', help='Download all updates matching filter to the cache')
def download(parser, context, args):
    parser.add_argument('--product', help="Product name or guid to download updates for")
    parser.add_argument('--product-family', help="Product family or guid to download updates for")
    args = parser.parse_args(args)

    if args.product and args.product_family:
        exit(1)

    if args.product:
        downloader.update_product(args.product)


if __name__ == '__main__':
    handler = ArgumentHandler()
    handler.run()
