import json

import requests
import re

REGEX_KBID = re.compile(r"KB(\d+)")
REGEX_NAME = re.compile(r"ScopedViewHandler_titleText\">([^<]+)</")
REGEX_DOWNLOAD = re.compile(r"downloadInformation\[0\]\.files\[(\d+)\]\.([^ ]+) = \'([^']+)\'")


def get_update_details(guid):
    url = 'http://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid={}'.format(guid)
    details = requests.get(url)
    name = REGEX_NAME.search(details.content.decode()).group(1)
    kb = int(REGEX_KBID.search(name).group(1))
    return name, kb


def get_download_urls(guid):
    url = 'http://www.catalog.update.microsoft.com/DownloadDialog.aspx'
    json_blob = [{
        'size': 0,
        'languages': '',
        'uidInfo': guid,
        'updateID': guid
    }]
    formdata = {
        'updateIDs': json.dumps(json_blob),
        'updateIDsBlockedForImport': '',
        'wsusApiPresent': '',
        'contentImport': '',
        'sku': '',
        'serverName': '',
        'ssl': '',
        'portNumber': '',
        'version': ''
    }

    response = requests.post(url, data=formdata)
    html = response.content.decode()
    downloads = {}
    for line in REGEX_DOWNLOAD.findall(html):
        download_id, key, value = line
        if download_id not in downloads:
            downloads[download_id] = {}
        downloads[download_id][key] = value
    return list(downloads.values())
