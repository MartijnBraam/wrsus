from peewee import *

db = SqliteDatabase('storage/update.db')


class Company(Model):
    guid = CharField(max_length=32)
    name = CharField(null=True)

    class Meta:
        database = db


class ProductFamily(Model):
    guid = CharField(max_length=32)
    name = CharField(null=True)

    class Meta:
        database = db


class Product(Model):
    guid = CharField(max_length=32)
    name = CharField(null=True)

    class Meta:
        database = db


class UpdateClassification(Model):
    guid = CharField(max_length=32)
    name = CharField(null=True)

    class Meta:
        database = db


class Update(Model):
    guid = CharField(max_length=32, index=True)
    revision = CharField(max_length=32)
    revision_number = IntegerField()
    creation_date = DateTimeField()

    company = ForeignKeyField(Company, related_name='updates', null=True)
    product_family = ForeignKeyField(ProductFamily, related_name='updates', null=True)
    classification = ForeignKeyField(UpdateClassification, related_name='updates', null=True)

    active = BooleanField(default=True)

    class Meta:
        database = db


class ProductToUpdate(Model):
    product = ForeignKeyField(Product)
    update = ForeignKeyField(Update)

    class Meta:
        database = db
        primary_key = CompositeKey('product', 'update')


class Prerequisite(Model):
    update = ForeignKeyField(Update, related_name='prerequisites')

    class Meta:
        database = db


class PrerequisiteUpdate(Model):
    prerequisite = ForeignKeyField(Prerequisite, related_name='updates')
    update = ForeignKeyField(Update)

    class Meta:
        database = db
        primary_key = CompositeKey('prerequisite', 'update')


class File(Model):
    uid = CharField(unique=True)
    url = CharField()
    downloaded = BooleanField(default=False)

    class Meta:
        database = db


class UpdateFile(Model):
    update = ForeignKeyField(Update, related_name='files')
    file = ForeignKeyField(File)

    class Meta:
        database = db
        primary_key = CompositeKey('update', 'file')


db.create_tables(
    [Company, ProductFamily, Product, UpdateClassification, Update, ProductToUpdate, Prerequisite, PrerequisiteUpdate,
     File, UpdateFile],
    safe=True)
