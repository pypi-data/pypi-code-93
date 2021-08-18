# coding=utf-8
import os
import filecmp
import itertools


class fdups:

    def __init__(self, list_of_dirs = []):
        self.exclude = {'Thumbs.db'}
        self.set(list_of_dirs)

    def set(self, list_of_dirs):
        self.list_of_dirs = list_of_dirs
        self.files = []
        self.filecount = 0
        self.wasted_space = 0
        self.dups = []


    def naturalsize(self, value, format='%.1f'):
        """This function is from the humanize-0.5.1 package with some changes.
        You can find the package here - https://github.com/jmoiron/humanize
        It makes the file size numbers more readable."""

        suffix = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        base = 1024
        bytes = float(value)

        if bytes == 1: return '1 Byte'
        elif bytes < base: return '%d Bytes' % bytes

        for i,s in enumerate(suffix):
            unit = base ** (i+2)
            if bytes < unit:
                return (format + ' %s') % ((base * bytes / unit), s)

        return (format + ' %s') % ((base * bytes / unit), s)

        
    def join(self, a, b):
        """Joins paths"""
        return a + '\\' + b


    def docmp(self, samesize):
        """Takes a list of files with the same size and compares them to one another
        to form groups of identical files."""
        
        grp = []

        for c in itertools.combinations(samesize, 2):
            foundgroup = False
            #print c
            if filecmp.cmp(self.join(c[0][0], c[0][1]), 
                           self.join(c[1][0], c[1][1]), shallow = False):
                for gr in grp:
                    if (c[0] in gr) or (c[1] in gr):
                        foundgroup = True
                        if (c[0] not in gr): gr.append(c[0])
                        if (c[1] not in gr): gr.append(c[1])
                        break
                if not foundgroup:
                    grp.append(list(c))

        print '.',

        return grp



    def see_groups(self):
        """Shows the duplicate groups"""
        for dup in self.dups:
            print '\n'
            for dp in dup:
                print self.join(dp[0], dp[1])



    def fdups(self):
        """Adds all files from all folders into a list that consists of tuples in the form 
                    [(dir, fname, size), (dir, fname, size), ...]
        sorts the files by size and sends those that have the same size to docmp()
        to be compared to one another. If the function finds any files that are identical
        they are added to self.dups which is a list of lists of tuples of identical files.
        """
        if not self.list_of_dirs: 
            print 'No dirs set'
            return
        if self.dups:
            print 'Already found the dups.'
            return

        print 'Collecting files'
        for d in self.list_of_dirs:
            if os.path.isfile(d):
                self.files.append((d[:d.rfind("\\")], d[d.rfind("\\")+1:], os.path.getsize(d)))
                #print self.files[-1]
            else:
                if d[-1] == "\\": d = d[:-1]
                for curdir, subdirs, filenames in os.walk(unicode(d)):
                    #print curdir
                    for fname in filenames:
                        #print('\t%s' % fname)
                        if fname not in self.exclude:
                            fullpath = curdir + '\\' + fname
                            self.files.append((curdir, fname, os.path.getsize(fullpath)))

        if not self.files: return
        self.filecount = len(self.files)

        print 'Sorting'
        self.files.sort(key = lambda x: x[2])
        prev = self.files[0]
        temp = []
        print 'Comparing'
        for f in self.files[1:]:
            if (prev[2] == f[2]):
                if (temp == []):
                    temp.append(prev)
                temp.append(f)
            if (prev[2] != f[2]) or (f == self.files[-1]):
                if (temp != []):
                    dc = self.docmp(temp)
                    if (dc != []):
                        self.dups.extend(dc)
                        for dc_ in dc:
                            self.wasted_space = self.wasted_space + (len(dc_) - 1)*dc_[0][2]
                    temp = []
            prev = f


        for dup in self.dups:
            for dp in dup:
                self.files.remove(dp)

        print '\nInfo:'
        print 'Total number of files compared: ', self.filecount
        print 'Non duplicate files: ', len(self.files)
        print 'Duplicate groups: ', len(self.dups)
        print 'Total wasted space: ', self.naturalsize(self.wasted_space), '  (',self.wasted_space,')'

        print '\nDo you want to see the duplicate groups?'
        print "(y for Yes, anything else for No)"
        if raw_input() == 'y':
            self.see_groups()

        print '\nDo you want to see the NON duplicate files? (' + str(len(self.files)) + ' files)'
        print "(y for Yes, anything else for No)"
        if raw_input() == 'y':
            for f in self.files:
                print self.join(f[0], f[1])

























