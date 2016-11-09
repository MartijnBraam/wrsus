import subprocess
import os
import tqdm

import requests


def fetch(url, target, force=False):
    target = 'storage/' + target
    if not force and os.path.isfile(target):
        return target

    directory = os.path.dirname(target)

    r = requests.get(url, stream=True)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    chunk_size = 1024
    filesize = int(r.headers['content-length'])
    with open(target, 'wb') as f:
        for chunk in tqdm.tqdm(r.iter_content(chunk_size=chunk_size), total=filesize / chunk_size, unit='kB'):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return target


def cabextract(cab_file, file_to_extract, target):
    cab_file = 'storage/' + cab_file
    target = 'storage/' + target
    command = ['cabextract', '-q', '-F', file_to_extract, cab_file]
    subprocess.call(command, stderr=subprocess.DEVNULL)
    os.rename(file_to_extract, target)
