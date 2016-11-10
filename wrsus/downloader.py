import wrsus.database as db
import wrsus.tools as tools
from wrsus.detail_fetcher import get_update_details, get_download_urls

import posixpath
import urlparse3


def update_product(identifier):
    product = db.Product.select().where(db.Product.name == identifier).get()

    updates = db.Update.select().join(db.ProductToUpdate).where(
        db.ProductToUpdate.product == product)
    updates = list(updates)
    for update in updates:
        if not update.name:
            name, kbid = get_update_details(update.guid)
            update.name = name
            update.kbid = kbid
            update.save()

        print(update.name)

        files = get_download_urls(update.guid)

        for file in files:
            filename = 'updates/KB{}/{}'.format(update.kbid, file['fileName'])
            tools.fetch(file['url'], filename, description=file['fileName'])


def url_to_filename(url):
    path = urlparse3.parse_url(url).path
    filename = posixpath.basename(path)
    return filename
