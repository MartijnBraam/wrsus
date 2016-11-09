from tqdm import tqdm

import wrsus.tools as tools
import wrsus.package_xml_iterator as pxi
import wrsus.database as db
import wrsus.datastructures as datastructures
import wrsus.tables as tables

import logging
import datetime


def get_catalog():
    url = 'http://download.windowsupdate.com/microsoftupdate/v6/wsusscan/wsusscn2.cab'

    logging.info('Downloading update catalog')
    tools.fetch(url, 'wsus/wsusscn2.cab')
    logging.info('Extracting catalog')
    tools.cabextract('wsus/wsusscn2.cab', 'package.cab', 'wsus/package.cab')
    tools.cabextract('wsus/package.cab', 'package.xml', 'wsus/package.xml')


def build_package_database():
    logging.info('Switching database to async exclusive for performance')
    db.db.execute_sql('PRAGMA journal_mode=wal;')
    db.db.execute_sql('PRAGMA synchronous=0;')
    db.db.execute_sql('PRAGMA locking_mode=EXCLUSIVE;')

    logging.info('Building package database phase 1')
    cache = {
        'company': {None: None},
        'product': {None: None},
        'product_family': {None: None},
        'classification': {None: None}
    }
    for ob in tqdm(pxi.iterate(), desc='Parsing XML Tree (around 180.000 items)'):
        if isinstance(ob, datastructures.Update):
            with db.db.atomic() as transaction:
                update_date = datetime.datetime.strptime(ob.creation_date, '%Y-%m-%dT%H:%M:%SZ')

                if ob.company_id and ob.company_id not in cache['company']:
                    company = db.Company.create(guid=ob.company_id, name=lookup_guid_name(ob.company_id))
                    cache['company'][ob.company_id] = company

                if ob.product_family_id and ob.product_family_id not in cache['product_family']:
                    product_family = db.ProductFamily.create(guid=ob.product_family_id,
                                                             name=lookup_guid_name(ob.product_family_id))
                    cache['product_family'][ob.product_family_id] = product_family

                if ob.classification_id and ob.classification_id not in cache['classification']:
                    classification = db.UpdateClassification.create(guid=ob.classification_id,
                                                                    name=lookup_guid_name(ob.classification_id))
                    cache['classification'][ob.classification_id] = classification

                active = True
                if len(ob.superseded_by) > 0:
                    active = False

                update = db.Update.create(guid=ob.update_id, revision=ob.revision_id, revision_number=ob.revision,
                                          creation_date=update_date, company=cache['company'][ob.company_id],
                                          classification=cache['classification'][ob.classification_id],
                                          product_family=cache['product_family'][ob.product_family_id], active=active)

                if len(ob.product_id) > 0:
                    for prod in ob.product_id:
                        if prod not in cache['product']:
                            product = db.Product.create(guid=prod, name=lookup_guid_name(prod))
                            cache['product'][prod] = product

                        db.ProductToUpdate.create(product=cache['product'][prod], update=update)

        if isinstance(ob, datastructures.FileLocation):
            db.File.create(uid=ob.file_id, url=ob.url)

    totalUpdates = db.Update.select().count()

    del cache

    logging.info('Building update graph')
    with db.db.atomic() as transaction:
        for ob in tqdm(pxi.iterate(), desc='Building update graph', total=totalUpdates, unit=' Updates'):
            if isinstance(ob, datastructures.Update):
                update = db.Update.get(db.Update.guid == ob.update_id and db.Update.revision == ob.revision_id)

                for prerequisite_group in ob.prerequisites:
                    db_prereq = db.Prerequisite.create(update=update)

                    for prerequisite in prerequisite_group.updates:
                        prereq_update = db.Update.get(db.Update.guid == prerequisite)

                        db.PrerequisiteUpdate.create(prerequisite=db_prereq, update=prereq_update)

                if len(ob.payload_files) > 0:
                    for file in ob.payload_files:
                        file_row = db.File.get(db.File.uid == file)
                        db.UpdateFile.create(update=update, file=file_row)


def lookup_guid_name(guid):
    if guid in tables.guid_name:
        return tables.guid_name[guid]
    else:
        return None
