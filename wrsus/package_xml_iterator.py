import xml.etree.cElementTree as elementtree

from wrsus.datastructures import Update, Prerequisite, FileLocation

yield_object = None


def iterate():
    global yield_object
    contents = elementtree.iterparse(open('storage/wsus/package.xml'), events=("start", "end"))
    context = None
    for event, element in contents:
        if '}' in element.tag:
            element.tag = element.tag.split('}', 1)[1]

        if event == 'start' and element.tag == 'Update':
            context = 'update'
            UpdateProcessor.process(event, element)
        elif event == 'end' and element.tag == 'Update':
            UpdateProcessor.process(event, element)
            context = None
            element.clear()
        elif event == 'start' and element.tag == 'FileLocations':
            context = 'files'
        elif event == 'end' and element.tag == 'FileLocations':
            context = None
        else:
            if context == 'update':
                UpdateProcessor.process(event, element)
            elif context == 'files':
                if event == 'start' and element.tag == 'FileLocation':
                    file = FileLocation()
                    file.file_id = element.attrib['Id']
                    file.url = element.attrib['Url']
                    yield file
                    element.clear()

        if yield_object:
            yield yield_object.current
            yield_object = None


class UpdateProcessor:
    current = None

    prereq_path = None

    in_superseded = False

    @staticmethod
    def process(event, element):
        global yield_object
        if event == 'start' and element.tag == 'Update':
            UpdateProcessor.current = Update()
            UpdateProcessor.current.update_id = element.attrib['UpdateId']
            UpdateProcessor.current.revision = int(element.attrib['RevisionNumber'])
            UpdateProcessor.current.revision_id = element.attrib['RevisionId']
            UpdateProcessor.current.creation_date = element.attrib['CreationDate']

        if event == 'start' and element.tag == 'File':
            UpdateProcessor.current.payload_files.append(element.attrib['Id'])

        if event == 'start' and element.tag == 'Language':
            UpdateProcessor.current.languages.append(element.attrib['Name'])

        if event == 'start' and element.tag == 'Or':
            UpdateProcessor.prereq_path = Prerequisite()

        if event == 'end' and element.tag == 'Or':
            UpdateProcessor.current.prerequisites.append(UpdateProcessor.prereq_path)
            UpdateProcessor.prereq_path = None

        if event == 'start' and element.tag == 'UpdateId':
            uid = element.attrib['Id']
            if UpdateProcessor.prereq_path:
                UpdateProcessor.prereq_path.updates.append(uid)
            else:
                temp = Prerequisite()
                temp.updates.append(uid)
                UpdateProcessor.current.prerequisites.append(temp)

        if event == 'start' and element.tag == 'Category':
            ctype = element.attrib['Type']
            value = element.attrib['Id']
            if ctype == 'Company':
                UpdateProcessor.current.company_id = value
            elif ctype == 'Product':
                UpdateProcessor.current.product_id.append(value)
            elif ctype == 'ProductFamily':
                UpdateProcessor.current.product_family_id = value
            elif ctype == 'UpdateClassification':
                UpdateProcessor.current.classification_id = value

        if element.tag == 'SupersededBy':
            UpdateProcessor.in_superseded = event == 'start'

        if event == 'start' and element.tag == 'Revision':
            if UpdateProcessor.in_superseded:
                UpdateProcessor.current.superseded_by.append(element.attrib['Id'])

        if event == 'end' and element.tag == 'Update':
            yield_object = UpdateProcessor
