import os, traceback
from sys import exit, argv
from difflib import SequenceMatcher

class Noter:

    def __init__(self, configfile, search):
        self.search = search
        self.file = configfile
        self.file1 = self.open_file()
        self.note = ''
        self.partial = ''
        self.notes = []

    def open_file(self):
        return open(self.file, 'r')

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
        for line in self.file1.readlines():
            self.determine(line)

        # Create last pair
        self.create_pair()

    def similar(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def return_notes(self):
        for note in self.notes:
            note, notetext = note
            similiar = self.similar(note, self.search)

            if similiar > 0.75:
                print '``{}\n{}'.format(note, notetext)
                print '-'*15, '\n'

    def main(self):
        self.loop_file()
        self.return_notes()


if __name__ == '__main__':
    try:
        noter = Noter(argv[1], ' '.join(argv[2:]))
        noter.main()
        exit(0)
    except KeyboardInterrupt, e:
        raise e
    except SystemExit, e:
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)