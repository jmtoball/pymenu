#!/usr/bin/python

from completer import PyMenuCompletions
from gui import PyMenuGUI

if __name__ == '__main__':
    model = PyMenuCompletions()
    gui   = PyMenuGUI(model)
