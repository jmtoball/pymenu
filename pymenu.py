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
        return set(executables)

    def getAllExecutables(self):
        return self.getExecutables(self.binpaths)

    def completeCommand(self, name):
        #TODO Regex-Matching
        commandfilter = lambda x: x.startswith(name)
        return filter(commandfilter, self.getAllExecutables())

    def completePath(self, path):
        head, tail = os.path.split(path)
        fullPath = self.path
        if head:
            fullPath = os.path.join(self.path, head)
        #TODO Regex-Matching
        pathfilter = lambda x: x.startswith(tail)
        return filter(pathfilter, os.listdir(fullPath))

    def complete(self, tocomplete):
        completion = self.completeCommand(tocomplete)
        if completion:
            return completion
        else:
            return self.completePath(tocomplete)


from tkinter import *

class PyMenuGUI:

    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root, bg='black', width=self.root.winfo_screenwidth(), height=25)
        self.frame.pack_propagate(False)
        self.frame.pack()

        self.prompt = Entry(self.frame)
        self.prompt.focus_set()
        self.prompt.pack(side=LEFT)

        self.completions = Frame(self.frame, bg='black')

        self.refill(model.completeCommand('dir'))
        self.root.overrideredirect(True)
        self.root.focus_set()
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.root.mainloop()

    def refill(self, completions):
        for completion in self.completions.winfo_children():
            completion.destroy()

        for completion in completions:
            label = Label(self.completions, fg='white', text=completion)
            label.pack(side=LEFT, padx=5)
        self.completions.pack(side=LEFT, padx=25)

if __name__ == '__main__':
    model = PyMenuCompletions()
    gui   = PyMenuGUI()
