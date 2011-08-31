"""config.py: Config file for pyaudioslave."""


import os
from string import Template
import pyechonest.config as config

# Location to store temporary WAV files
TEMP_PREFIX = "/tmp"

# EchoNEST configuration variables
config.ECHO_NEST_API_KEY = '' #Get ECHONEST API key from here: http://developer.echonest.com/
config.CODEGEN_BINARY_OVERRIDE = os.path.abspath("/usr/local/bin/echoprint-codegen")

# libmagic identification strings for supported formats
SUPPORTED_TYPES = {'mp3' : ['MPEG ADTS, layer III, v1',
                           'Audio file with ID3 version 2'],
                   'm4a' : ['ISO Media, MPEG v4 system, iTunes AAC-LC',
                           'ISO Media, MPEG v4 system, version',
                           'MPEG ADTS, AAC',],
                   'flac': ['FLAC audio bitstream data',],
                   'wav' : ['RIFF (little-endian) data, WAVE audio',]}

# Media decoder templates
DECODE_TO_WAV = {'mp3' : Template('mpg123 -q -w "$wavefile" "$sourcefile"'),
                 'm4a' : Template('faad -q -o "$wavefile" "$sourcefile"'),
                 'flac': Template('flac -f --totally-silent -d "$sourcefile" -o "$wavefile"'),}

# Media encoder templates
ENCODE_FROM_WAV = {'mp3' : Template('lame --quiet -V3  $tags "$wavefile" "$destfile"'),
                   'm4a' : Template('faac -w $tags -o "$destfile" "$wavefile"'),
                   'flac': Template('flac -f --totally-silent $tags "$wavefile" -o "$destfile"'),}

# Media encoder tagging templates
ENCODE_TAGS =   {'album':               {'mp3' : '--tl "$value"',
                                         'm4a' : '--album "$value"',
                                         'flac': '--tag=ALBUM="$value"',},
                'comment':              {'mp3' : '--tc "$value"',
                                         'm4a' : '--comment "$value"',
                                         'flac': '--tag=DESCRIPTION="$value"',},
                'genre':                {'mp3' : '--tg "$value"',
                                         'm4a' : '--genre "$value"',
                                         'flac': '--tag=GENRE="$value"',},
                'performer':            {'mp3' : '--ta "$value"',
                                         'm4a' : '--artist "$value"',
                                         'flac': '--tag=PERFORMER="$value"',},
                'title':                {'mp3' : '--tt "$value"',
                                         'm4a' : '--title "$value"',
                                         'flac': '--tag=TITLE="$value"',},
                'track_name_position':  {'mp3' : '--tn "$value"',
                                         'm4a' : '--track "$value"',
                                         'flac': '--tag=TRACKNUMBER="$value"',},
                'recorded_date':        {'mp3' : '--ty "$value"',
                                         'm4a' : '--year "$value"',
                                         'flac': '--tag=DATE="$value"',}}

if not config.ECHO_NEST_API_KEY:
    Exception("EHONEST_API_KEY required")