class Update:
    def __init__(self):
        self.creation_date = None
        self.update_id = None
        self.revision = None
        self.revision_id = None

        self.company_id = None
        self.product_id = []
        self.product_family_id = None
        self.classification_id = None

        self.prerequisites = []
        self.payload_files = []

        self.languages = []

        self.superseded_by = []

    def __repr__(self):
        return '<Update {} rev. {}>'.format(self.update_id, self.revision)


class Prerequisite:
    def __init__(self):
        self.updates = []


class FileLocation:
    def __init__(self):
        self.file_id = None
        self.url = None
