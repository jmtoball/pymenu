import os
import stat

class PyMenuCompletions:

    path = "."
    binpaths = os.environ['PATH'].split(':')

    def getExecutables(self, paths):
        executables = []
        executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        for dir in paths:
            for filename in os.listdir(dir):
                path = os.path.join(dir,filename)
                if os.path.isfile(path) and os.stat(path).st_mode & executable:
                    executables.append(filename)
        return executables

    def getAllExecutables(self):
        return self.getExecutables(self.binpaths)

    def completeCommand(self, name):
        commandfilter = lambda x: x.startswith(name)
        return filter(commandfilter, self.getAllExecutables())

    def completePath(self, path):
        head, tail = os.path.split(path)
        fullPath = self.path
        if head:
            fullPath = os.path.join(self.path, head)
        pathfilter = lambda x: x.startswith(tail)
        return filter(pathfilter, os.listdir(fullPath))

    def complete(self, tocomplete):
        completion = self.completeCommand(tocomplete)
        if completion:
            return completion
        else:
            return self.completePath(tocomplete)
