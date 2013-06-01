import os

class PyMenu:

    path = "."

    def completePath(self, path):
        head, tail = os.path.split(path)
        print "---"
        print "head:"+ head
        print "tail:"+ head
        print "completed: "+ os.path.join(self.path, head)
        print "---"
        fullPath = self.path
        if head:
            fullPath = os.path.join(self.path, head)
        pathfilter = lambda x: x.startswith(tail)
        return filter(pathfilter, os.listdir(fullPath))
