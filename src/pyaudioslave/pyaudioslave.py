#!/usr/bin/env python

"""pyaudioslave.py: Transcode and fingerprint your audio files with Python."""

__author__    = "Paul Pietkiewicz"
__copyright__ = "Copyright 2011, Paul Pietkiewicz"
__email__     = "pawel.pietkiewicz@gmail.com"
__version__   = '0.892'

import os
import shlex
import shutil
import tempfile
import subprocess
import sys
import argparse
import pyechonest.song as song
from string import Template
from pprint import pprint
from magic import Magic
from pymediainfo import MediaInfo

from utils import setup_dest_path
from config import SUPPORTED_TYPES, DECODE_TO_WAV, ENCODE_FROM_WAV, \
                   ENCODE_TAGS, TEMP_PREFIX

class AudioSlaveException(Exception):
    """Generic AudioSlave Error"""
    
    def __str__(self):
        return self.args[0]

class AudioSlave:
    """Audio file class with transcoding & music fingerprinting capabilities."""
    
    def __init__(self, file_path, should_cache_wav=False, echoprint=False,
                 echoprint_tags=False, echoprintQuickMode=True):
        """Create the AudioSlave class.
        
        Keyword arguments:
        file_path -- the source file
        should_cache_wav -- should the decoded wave file by cached
        echoprint -- should the audiofile be fingerprinted during instantiation
        echoprint_tags -- should the echoprint audio tags be pulled durring
                         instantiation
        echoprintQuickMode -- True ensures 30 second echoprint for ID, False
                          ensures full song echoprint (NOTE: can crash for VERY
                          long songs / DJ sets)
        
        NOTE: echoprint_tags parameter overwrites echoprint
        """

        if os.path.exists(file_path):
            self.sourcefile = os.path.abspath(file_path)
        else:
            raise AudioSlaveException("Source file %s does not exist!" % file_path)
        
        self.file_type = self._get_type()
        self.tag_dict = self._get_tags()
        self.should_cache_wav = should_cache_wav
        
        if self.file_type == 'wav':
            self.wavefile = self.sourcefile
            self.wave_temp = False
        else:
            self.wavefile = None
            self.wave_temp = None

        self.echoprintQuickMode = echoprintQuickMode
        
        self.echoprint_code = None
        if echoprint:
            self.echoprint_codegen()
        
        self.echoprint_tags = None
        if echoprint_tags:
            self.update_echonest_tags()
            
        # Used to store the locations of transcoded files
        self.trancoded_files = {}
    
    def __del__(self):
        try:
            if not self.should_cache_wav and self.wave_temp and \
               os.path.exists(self.wavefile):
                os.unlink(self.wavefile)
        except:
            pass
    
    #
    # Internal Utility Functions
    #
        
    def _get_type(self, file_path=None):
        """Returns the file_type of the classes source media file or the type
           of the provided file."""
        
        if not file_path:
            file_path = self.sourcefile
            
        magic = Magic()
        file_type =  magic.from_file(file_path)
        for media_type in SUPPORTED_TYPES.keys():
            for file_string in SUPPORTED_TYPES[media_type]:
                if file_string in file_type:
                    return media_type
        
        raise AudioSlaveException("File type '%s' not supported!" % file_type)

    def _get_tag_param_str(self, dest_format):
        """Generates the tag parameter string for encoders provided the
           destination format."""
        
        tag_string = ''
        if self.tag_dict != {}:
            tag_list = []
            for tag in self.tag_dict.keys():
                tag_list.append(Template(ENCODE_TAGS[tag][dest_format]).substitute(value=self.tag_dict[tag]))
            tag_string = " ".join(tag_list)
        
        return tag_string
     
    def _get_tags(self):
        """Returns the tag info of the associated source file."""

        result_dict = {}        
        media_info = MediaInfo.parse(self.sourcefile)
        if hasattr(media_info, 'tracks') \
            and type(media_info.tracks) == type([]) \
            and len(media_info.tracks):
            for entry in ENCODE_TAGS.keys():
                try:
                    value = getattr(media_info.tracks[0], entry)
                    if value != None:
                        result_dict[entry] = value
                except AttributeError:
                    pass

        return result_dict
    
    def _get_dest_path(self, dest_format, destination_path=None):
        """
        Returns a destination path for the transcoded file.
        Ensures directories are created.
        """
           
        if not destination_path:
            # Use sourcefile path
            destination_path = "%s.%s" % (os.path.splitext(self.sourcefile)[0], dest_format)
        else:
            if destination_path.endswith('/') or not destination_path.endswith(tuple(SUPPORTED_TYPES.keys())):
                destination_path = "%s.%s" % (os.path.join(destination_path, os.path.splitext(os.path.split(self.sourcefile)[1])[0]), dest_format)
                setup_dest_path(destination_path)
            elif '/' in destination_path and destination_path.endswith(tuple(SUPPORTED_TYPES.keys())):
                setup_dest_path(destination_path)
        return destination_path
        
    def _get_preexisting(self, dest_format, destination_path):
        """
        Returns a path to a transcoded file if transcoded previously. Copy
        file to provided destination path if different from original
        transcoded file path.
        """
        
        if dest_format in self.trancoded_files and \
           os.path.exists(self.trancoded_files[dest_format]):
            # Hey what do you know, we already transcoded it!
            if destination_path and destination_path == self.trancoded_files[dest_format]:
                return self.trancoded_files[dest_format]
            else:
                shutil.copy(self.trancoded_files[dest_format], destination_path)
                return destination_path
        # If not found
        return None
    
    def _decode(self, destination_path=None):
        """
        Transcode sourcefile to WAV file. By default use temporary WAV file
        path, optionally transcode to provided path.
        """
           
        if self.wavefile and os.path.exists(self.wavefile):
            # WAV file already exists, no need to decode
            if self.wavefile == destination_path:
                return self.wavefile
            else:
                setup_dest_path(destination_path)
                shutil.copy(self.wavefile, destination_path)
                return destination_path
        
        if not destination_path:
            destination_path= tempfile.mkstemp(dir=TEMP_PREFIX)[1]
            self.wave_temp = True
        else:
            setup_dest_path(destination_path)
            self.wave_temp = False
                    
        if self.file_type in DECODE_TO_WAV:
            command_line = DECODE_TO_WAV[self.file_type].substitute(sourcefile=self.sourcefile, \
                                                                 wavefile=destination_path)
            command_list = shlex.split(command_line)
            with open('/dev/null', 'w') as DEVNULL:
                returncode = subprocess.call(command_list, stdout=DEVNULL, stderr=DEVNULL)
            if returncode == 0:
                # If Successful
                self.wavefile = os.path.abspath(destination_path)
                return os.path.abspath(destination_path)
        
        self.wave_temp = None
        raise AudioSlaveException("Problem decoding wave file.")
    
    def _encode(self, dest_format, destination_path):
        """Transcode self.wavefile to requested format at provided path."""
        
        if not self.wavefile:
            self._decode()

        tags = self._get_tag_param_str(dest_format) 
        command_line = str(ENCODE_FROM_WAV[dest_format].substitute(wavefile=self.wavefile, \
                                                    tags=tags, \
                                                    destfile=destination_path))
        command_list = shlex.split(command_line)
        with open('/dev/null', 'w') as DEVNULL:
            returncode = subprocess.call(command_list, stdout=DEVNULL, stderr=DEVNULL)
        if returncode == 0 and os.path.exists(destination_path) and \
           self._get_type(destination_path) == dest_format:
            self.trancoded_files[dest_format] = destination_path
            return destination_path
        
        raise AudioSlaveException("Problem encoding/writing out file. HINT: Do we have permissions to write?")
     
     #
     # Accessors
     #
     
    def get_type(self):
        """Return media type of sourcefile"""
        
        return self.file_type
     
    def get_preexisting_transcodes(self):
        """Return dictionary of transcoded formats with paths to those files"""
        
        return self.trancoded_files
     
    def get_tags(self, echoprint=False):
        """Returns tags for the sourcefile. If echoprint is set to True, returns
           the echoprint tags"""
        
        if echoprint:
            if not self.echoprint_tags:
                self.update_echonest_tags()
            return self.echoprint_tags
        return self.tag_dict
    
    def get_echoprint_code(self):
        """Returns the echoprint code for the sourcefile."""
        
        if not self.echoprint_code:
            self.echoprint_codegen()
        return self.echoprint_code

     
    #
    # Transcoding
    #
     
    def transcode (self, dest_format, destination_path=None):
        """Transcode the source file.
        
        Keyword arguments:
        dest_format -- destination format for the media
        destination_path -- destination path for the media
                           (by default same location and filename as source)
        """
        
        if not dest_format.lower() in SUPPORTED_TYPES.keys():
            msg = "Destination media format '%s' not supported!" % dest_format
            raise AudioSlaveException(msg)
            
        destination_path = self._get_dest_path(dest_format, destination_path)
        
        # Check if we already have the transcoded file ready to go
        preexisting = self._get_preexisting(dest_format, destination_path)
        if preexisting:
            return preexisting

        if not self.wavefile:
            if dest_format == 'wav':
                #We have less work if we're going to WAV
                self._decode(destination_path)
                return destination_path
            # Make a temporary WAV file
            self._decode()
            self.wave_temp = True
        
        return self._encode(dest_format, destination_path)
        
    #
    # Echoprint Fingerprinting / Tagging
    #
     
    def echoprint_codegen(self):
        """Create and store echoprint code"""
        
        # Fragments taken from echonest's echonest-codegen lookup.py script
        if self.echoprintQuickMode:
            # echoprintQuickMode --> reads just the first 30 seconds of the file
            fp = song.util.codegen(self.sourcefile)
        else:
            fp = song.util.codegen(self.sourcefile, start=-1, duration=-1)

        if len(fp) and "code" in fp[0]:
            self.echoprint_code = fp
        else:
            msg = "Could not extract echonest code! HINT: check if config.CODEGEN_BINARY_OVERRIDE is pointing to echoprint-codegen"
            raise AudioSlaveException(msg)
    
    def update_echonest_tags(self):
        """Obtain echoprint tags (if exist) for sourcefile. Generate echoprint
           code if required"""
           
        # Fragments taken from echonest's echonest-codegen lookup.py script
        if not self.echoprint_code:
            self.echoprint_codegen()
        
        # The version parameter to song/identify indicates the use of echoprint
        result = song.identify(query_obj=self.echoprint_code, version="4.11")
        if len(result):
            self.echoprint_tags = result


def main():
    """CLI Driver"""
    parser = argparse.ArgumentParser(description='Audio Transcoder', \
                                     prog='pyaudioslave.py')
    subparsers = parser.add_subparsers()
    
    transcode_parser = subparsers.add_parser('transcode')
    transcode_parser.add_argument('transcodeSource', help='File to transcode')
    transcode_parser.add_argument('dest_format', help='Destination format', \
                                 type=str, choices=SUPPORTED_TYPES.keys())
    transcode_parser.add_argument('-d', '--dest', dest='destination_path', \
                                 help='Path to destination', action='store')
    
    fingerprint_parser = subparsers.add_parser('fingerprint')
    fingerprint_parser.add_argument('fingerprintSource', \
                                   help='File to fingerprint')
    fingerprint_parser.add_argument('-q', '--query', dest='query', \
                                   help='Query Echonest', action='store_true')
   
    args = parser.parse_args()
    
    if hasattr(args, 'transcodeSource'):
        afile = AudioSlave(args.transcodeSource)
        print "Source file type: %s" % afile.get_type()
        print "Destination file type : %s" % args.dest_format

        if args.destination_path:
            transcoded_file = afile.transcode(str(args.dest_format), \
                                             str(args.destination_path))
        else:
            transcoded_file = afile.transcode(str(args.dest_format))
        
        print "Transcoded to : %s" % transcoded_file
        sys.exit(0)

    
    elif hasattr(args, 'fingerprintSource'):
        afile = AudioSlave(args.fingerprintSource, echoprint=True)
        if args.query:
            result_tags = afile.get_tags(echoprint=True)
            if not result_tags:
                print "No matches found!"
            else:
                print "Title:  " + result_tags[0].title
                print "Artist: " + result_tags[0].artist_name
        else:
            pprint(afile.get_echoprint_code())
            
    else:
        print "ERROR: invalid mode. Use either 'transcode' or 'fingerprint'"
        sys.exit(1)
        raise Exception
    
if __name__ == "__main__":
    main()
    sys.exit(0)
