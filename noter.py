#!/usr/bin/env python2.7

import os, traceback, getpass
import sys
import argparse
from difflib import SequenceMatcher
import yaml
from get_config import get_or_create
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../accessdb')))
# from accessdb import accessDB


class Noter:

    def __init__(self, opt):
        self.opt = opt
        self.username = getpass.getuser()

        # Symlink causes issues with dirname, get realpath first.
        self.script_location = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        self.Database = '%s/noter.db' % self.script_location

        self.noter_location = self.get_personal_file()[1]
        self.noter_file = self.open_file(self.noter_location)

        self.search = opt.search
        self.note = ''
        self.partial = ''
        self.notes = []


    def get_personal_file(self):
        return get_or_create(self.Database, self.username)

    def open_file(self, notefile):
        return open(notefile, 'r')

    def create_pair(self):
        self.notes.append((self.note, self.partial.rstrip('\n')))
        self.note = ''
        self.partial = ''

    def add_note(self, line):
        self.note = line.lstrip('``').rstrip('\n')

    def add_partial(self, line):
        self.partial += line

    def determine(self, line):

        if line.startswith('``'):

            if self.note != "":
                self.create_pair()
                self.add_note(line)
            else:
                self.add_note(line)

        else:
            self.add_partial(line)

    def loop_file(self):
        for line in self.noter_file.readlines():
            self.determine(line)

        # Create last pair
        self.create_pair()

    def similar(self, a, b):
        # list( set( [ 1, 2 ] ).symmetric_difference( set( [ 2, 3 ] ) ) )
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


    def print_top(self, top):

        if top['top'] < self.opt.threshold:
            print 'The closest I could find is:\n'

        for item in top['matches']:
            print item['text']
            print '-'*15, '\n'


    def return_notes(self):
        top = {'top': 0, 'matches': []}
        for note in self.notes:
            notename, notetext = note

            similiar = self.similar(notename, self.search)
            text = '``{}\n{}'.format(notename, notetext)

            if similiar > top['top']:
                top['top'] = similiar
                top['matches'] = [{'value': similiar, 'text': text}]

            elif similiar > self.opt.threshold:
                if top >= self.opt.threshold:
                    top['matches'].append({'value': similiar, 'text': text})
                else:
                    top['matches'] = [{'value': similiar, 'text': text}]

        self.print_top(top)

    def main(self):
        self.loop_file()
        self.return_notes()


def get_options():
    opt = argparse.ArgumentParser(add_help=None, usage='Help')
    opt.add_argument("-h", "--help", action="store_true")
    opt.add_argument("-f", "--file", type=str)
    opt.add_argument("-t", "--threshold", type=float, default=0.75)
    opt.add_argument("search", type=str)
    return opt

def print_help(opt):
    print sys.exit(opt.print_help())


if __name__ == '__main__':
    try:
        o = get_options()
        options = o.parse_args()
        if options.help:
            print_help(o)
        noter = Noter(options)
        noter.main()
        sys.exit(0)
    except KeyboardInterrupt, e:
        raise e
    except SystemExit, e:
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
