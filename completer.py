import os
import stat
import difflib
from itertools import islice, count

class PyMenuCompletions:

    path = "."
    binpaths = os.environ['PATH'].split(':')
    commandcache = None
    pathmap = {}
    current = None
    lastComplete = None

    COMPLETE_CMD  = 0
    COMPLETE_PATH = 1

    def getExecutables(self, paths):
        executables = []
        executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        for dir in paths:
            if not os.path.isdir(dir):
                continue
            for filename in os.listdir(dir):
                path = os.path.join(dir,filename)
                if os.path.isfile(path) and os.stat(path).st_mode & executable:
                    executables.append(filename)
                    self.pathmap[filename] = os.path.join(dir, filename)
        return set(executables)

    def getAllExecutables(self):
        if not self.commandcache:
            self.commandcache = self.getExecutables(self.binpaths)
        return self.commandcache

    def judge(self, needle, haystack):
        case_sensitivity = 0
        if needle not in haystack:
            needle = needle.lower()
            haystack = haystack.lower()
            case_sensitivity = 1
        index = haystack.index(needle)
        overlap = len(haystack)-len(needle)
        return index + case_sensitivity + overlap/10.0

    def suggest(self, needle, haystack):
        filterfunc = lambda haystack: needle.lower() in haystack.lower()
        filtered = filter(filterfunc, haystack)
        keyfunc = lambda haystack: self.judge(needle, haystack)
        return sorted(filtered, key=keyfunc)

    def completeCommand(self, name):
        return self.suggest(name, self.getAllExecutables())

    def completePath(self, path):
        head, tail = os.path.split(path)
        fullPath = self.path
        if os.path.isabs(path):
            fullPath = head
        elif head:
            fullPath = os.path.join(self.path, head)
        return self.suggest(tail, os.listdir(fullPath))

    def getCurrent(self):
        return self.current

    def complete(self, toComplete, mode=None):
        if toComplete == self.lastComplete:
            return self.getCurrent()

        if mode == self.COMPLETE_PATH:
            completion = self.completePath(toComplete)
        else:
            completion = self.completeCommand(toComplete)
        self.current = completion
        self.lastComplete = toComplete
        return self.current

    def getPath(self, command):
        return self.pathmap.get(command)
