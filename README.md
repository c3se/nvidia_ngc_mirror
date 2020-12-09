# nvidia_ngc_mirror

Auto downloader of Nvidia NGC containers to local mirror.

Using predefined list of container urls combined with a "skip list" of old version tags 
that we do not want to download/mirror.

The container repos and tags are obtained from the `skopeo` program (https://github.com/containers/skopeo)
and the containers are pulled to disk using `singularity`, producing production ready singularity images.

The local file structure is a direct mirror of the package repository structure, and is used here
to detect already downloaded container tags. I.e. re-running this script will only download new
container tags not currently present on local disk.

*Author: Hugo U.R. Strand (2020)*
