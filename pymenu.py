import os
import stat
import difflib
from itertools import islice, count

class PyMenuCompletions:

    path = "."
    binpaths = os.environ['PATH'].split(':')
    commandcache = None
    pathmap = {}

    def getExecutables(self, paths):
        executables = []
        executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        for dir in paths:
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

    def completeCommand(self, name):
        commandfilter = lambda x: name in x
        return list(filter(commandfilter, self.getAllExecutables()))

    def completePath(self, path):
        head, tail = os.path.split(path)
        fullPath = self.path
        if os.path.isabs(path):
            print("absPath")
            fullPath = head
        elif head:
            print("path")
            fullPath = os.path.join(self.path, head)
        pathfilter = lambda x: tail in x
        return list(filter(pathfilter, os.listdir(fullPath)))

    def complete(self, tocomplete):
        completion = self.completeCommand(tocomplete)
        if len(completion):
            return completion
        else:
            return self.completePath(tocomplete)

    def getPath(self, command):
        return self.pathmap.get(command)


from tkinter import *
import subprocess

class PyMenuGUI:

    active = 0
    activetext = ""

    def __init__(self, model):
        self.model = model
        self.root = Tk()
        self.frame = Frame(self.root, bg='black', width=self.root.winfo_screenwidth(), height=25)
        self.frame.pack_propagate(False)
        self.frame.pack()

        self.prompt = Entry(self.frame, insertbackground='grey', bg='black', fg='white', relief=FLAT)
        self.prompt.bind('<KeyRelease>', self.complete)
        self.prompt.focus_set()
        self.prompt.pack(side=LEFT)

        self.completions = Frame(self.frame, bg='black')

        self.refill(model.completeCommand('dir'))
        self.root.update_idletasks()
        self.root.overrideredirect(True)
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.root.mainloop()

    def complete(self, event):
        key = repr(event.keysym)
        if key == "'Left'":
            self.active = abs(self.active-1)
        elif key == "'Right'":
            self.active = (self.active+1)%20
        elif key == "'Return'":
            self.exec()
        elif key == "'Tab'":
            self.prompt.delete(0, len( self.prompt.get()))
            self.prompt.insert(0, self.activetext)
            self.active = 0
        else:
            self.refill(self.model.complete(self.prompt.get()))

    def exec(self):
        call = self.prompt.get().split(" ")
        if len(call):
            cmd = call[0]
            path = model.getPath(cmd)
            subprocess.Popen([path]+call[1:])
            sys.exit(0)

    def refill(self, completions):
        for completion in self.completions.winfo_children():
            completion.destroy()

        i = 0
        for completion in islice(completions, 20):
            color = 'darkgrey'
            if i == self.active:
                color = 'darkblue'
                self.activetext = completion
            i += 1
            label = Label(self.completions, fg='white', bg=color, text=completion)
            label.pack(side=LEFT, padx=5)
        self.completions.pack(side=LEFT, padx=25)

if __name__ == '__main__':
    model = PyMenuCompletions()
    gui   = PyMenuGUI(model)
