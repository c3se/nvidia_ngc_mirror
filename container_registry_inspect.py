"""
Auto downloader of Nvidia NGC containers to local mirror.

Using predefined list of container urls combined with a "skip list" of old version tags 
that we do not want to download/mirror.

The container repos and tags are obtained from the `skopeo` program (https://github.com/containers/skopeo)
and the containers are pulled to disk using `singularity`, producing production ready singularity images.

The local file structure is a direct mirror of the package repository structure, and is used here
to detect already downloaded container tags. I.e. re-running this script will only download new
container tags not currently present on local disk.

Author: Hugo U.R. Strand (2020)

"""

import os
import json
from subprocess import check_output
from pathlib import Path

tmp_path = '/tmp/singularity/'
base_path = '/apps/nvidia-ngc-containers/'

# List of container repos in format (base url, container name, list of tags to skip)

packages = [
    ('nvcr.io/hpc/', 'gromacs', ['2016.4', '2018.2', '2020.2-arm64']),
    ('nvcr.io/hpc/', 'lammps', ['24Oct2018', 'patch23Oct2017', '15Jun2020-arm64']),
    ('nvcr.io/hpc/', 'namd', ['2.12-171025', '2.13b2-multinode', '2.13b2-singlenode', '3.0-alpha3-singlenode-arm64']),
    ('nvcr.io/nvidia/', 'pytorch', 
        ['17.10', '17.11', '17.12', 
         '18.01-py3', '18.02-py3', '18.03-py3', '18.04-py3', '18.05-py3', '18.06-py3', '18.07-py3', '18.08-py3', '18.09-py3', '18.10-py3', '18.11-py3', '18.12-py3', '18.12.1-py3', 
         '19.01-py3', '19.02-py3', '19.03-py3', '19.04-py3', '19.05-py3', '19.06-py3', '19.07-py3', '19.08-py3', '19.09-py3', '19.10-py3', '19.11-py3', '19.12-py3']),
    ('nvcr.io/nvidia/', 'tensorflow', 
        ['17.10', '17.11', '17.12', 
         '18.01-py2', '18.01-py3', '18.02-py2', '18.02-py3', '18.03-py2', '18.03-py3', '18.04-py2', '18.04-py3', '18.05-py2', '18.05-py3', '18.06-py2', '18.06-py3', 
         '18.07-py2', '18.07-py3', '18.08-py2', '18.08-py3', '18.09-py2', '18.09-py3', '18.10-py2', '18.10-py3', '18.11-py2', '18.11-py3', '18.12-py2', '18.12-py3', 
         '19.01-py2', '19.01-py3', '19.02-py2', '19.02-py3', '19.03-py2', '19.03-py3', '19.04-py2', '19.04-py3', '19.05-py2', '19.05-py3', '19.06-py2', '19.06-py3', 
         '19.07-py2', '19.07-py3', '19.08-py2', '19.08-py3', '19.09-py2', '19.09-py3', '19.10-py2', '19.10-py3', '19.11-tf1-py3', '19.11-tf2-py3', '19.12-tf1-py2', '19.12-tf1-py3', '19.12-tf2-py3' ]),
    ] 

# DEBUG
#packages = packages[4:]
print(packages)

downloads = dict()

for repo, package, skip_tags in packages:
    print(package)
    path = Path(base_path + package)
    print(path)
    path.mkdir(parents=True, exist_ok=True)

    # -- Get list of all available container tags using `skopeo`
    url = repo + package + ':' + skip_tags[0]
    cmd = f'skopeo inspect docker://{url}'
    print(cmd) 
    out = check_output(cmd, shell=True)
    out = json.loads(out)
    tags = out['RepoTags']
    #print(tags)
    tags = list(set(tags).difference(skip_tags))
    print(tags)

    # -- Filter tags with existing files on local disk
    image_tags = [ file.stem for file in path.glob('*.sif') ]
    print(f'image_tags = {image_tags}')
    tags = list(set(tags).difference(image_tags))
    print(tags)

    downloads[package] = tags

# -- Download absent container tags using `singularity pull`
for package, tags in downloads.items():
    print(package, tags)
    path = Path(base_path + package)
    for tag in tags:
        url = repo + package + ':' + tag
        filename = f'{tag}.sif'
        cmd = f'SINGULARITY_TMPDIR=/cephyr/NOBACKUP/priv/c3-staff/singularity_build' + \
              f' singularity pull {tmp_path}/{filename} docker://{url} && mv {tmp_path}/{filename} {path}/{filename}'
        print(cmd)
        os.system(cmd)
