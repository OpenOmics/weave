#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   Miscellaneous utility functions for caching 
#   pipeline resources
# ~~~~~~~~~~~~~~~
import subprocess
import json
import urllib.request
from argparse import ArgumentTypeError
from pathlib import Path
from urllib.parse import urlparse

from .config import remote_resource_confg
from .utils import esc_colors


parse_uri = lambda uri: (str(uri).split('://')[0], str(uri).split('://')[1]) if '://' in uri else None
info_download = lambda msg: print(esc_colors.OKGREEN + msg + esc_colors.ENDC)


class DownloadProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def valid_dir(path):
    """Validate path input for argument parsing

    Returns:
        (str): Absolute path to vetted output path
    """

    if Path(path).is_dir():
        return str(Path(path).absolute())
    elif not Path(path).exists():
        try:
            Path(path).mkdir(mode=0o777, parents=True)
        except:
            raise ArgumentTypeError(f"dir:{path} doesn't exist and can't be created")
        
        return str(Path(path).absolute())
    
    raise ArgumentTypeError(f"readable_dir:{path} is not a valid path")
    


def download(output_dir, local=False):
    """Download the resource bundle for 

    Returns:
        (bool): True if successful, False otherwise.
    """
    print(esc_colors.WARNING + 'Warning: cache download only implemented in serial local mode currently' + esc_colors.ENDC)
    #TODO: slurm implementation
    resources_to_download = json.loads(open(remote_resource_confg).read())

    for resource, uri in resources_to_download.items():
        protocol, url = parse_uri(uri)
        handle_download(output_dir, resource, protocol, url)

    print(esc_colors.OKGREEN + 'All resources downloaded!' + esc_colors.ENDC)

    return True


def handle_download(output_dir, resource, protocol, url):
    uri = protocol + "://" + url
    if protocol in ('http', 'https', 'ftp'):
        info_download(f"Getting web resource {resource}...")
        fnurl = Path(urlparse(url).path).stem
        try:
            import progressbar
            urllib.request.urlretrieve(uri, filename=Path(output_dir, fnurl), reporthook=DownloadProgressBar())
        except ModuleNotFoundError:
            print('Downloading resources....')
            urllib.request.urlretrieve(uri, filename=Path(output_dir, fnurl))
            print('....done.')

    elif protocol in ('docker'):
        info_download(f"Getting docker resource {resource}...")
        docker_tag = url.split('/')[-1]
        docker_v = docker_tag.split(':')[1]
        docker_name = docker_tag.split(':')[0]
        subprocess.check_call(['singularity', 'pull', '-F', f"{docker_name}_{docker_v}.sif", uri], cwd=output_dir)
    elif protocol in ('filelist'):
        info_download(f"Getting meta-resource {resource}...")
        file_list = urllib.request(url)
        for i, _file_uri in enumerate(file_list, start=1):
            this_protocol, this_url = parse_uri(_file_uri)
            print(f"\t Getting resource {str(i)} of {str(len(file_list))}")
            handle_download(output_dir, resource, this_protocol, this_url)
    else:
        raise ValueError(f"Unsupported resource protocol: {protocol}")
    return