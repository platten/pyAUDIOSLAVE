#!/usr/bin/env python

from distutils.core import setup
import sys
import glob

sys.path.append('./src')
from pyaudioslave.pyaudioslave import __version__ as audioslave_version

setup(
    name = 'pyAUDIOSLAVE',
    author       = 'Paul Pietkiewicz',
    author_email = 'pawel.pietkiewicz@gmail.com',
    description  = 'Transcode and fingerprint your audio files with Python',
    license      = 'PSF',
    keywords     = 'transcode fingerprint mp3 m4a aac flac tag',
    url          = 'https://github.com/platten/pyAUDIOSLAVE/',

    version          = audioslave_version,
    install_requires = ['pyechonest','pymediainfo','argparse', 'python-magic'],
    packages         = ['pyaudioslave'],
    package_dir      = {'pyaudioslave': 'src/pyaudioslave'},
    scripts          = glob.glob("bin/*")
)


