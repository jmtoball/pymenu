#!/usr/bin/python
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
            fullPath = head
        elif head:
            fullPath = os.path.join(self.path, head)
        pathfilter = lambda x: tail in x
        return list(filter(pathfilter, os.listdir(fullPath)))

    def getCurrent(self):
        return self.current

    def complete(self, toComplete):
        if toComplete == self.lastComplete:
            return self.getCurrent()
        completion = self.completeCommand(toComplete)
        if len(completion):
            self.current = completion
        else:
            self.current = self.completePath(toComplete)
        self.lastComplete = toComplete
        return self.current

    def getPath(self, command):
        return self.pathmap.get(command)

def hextorgb(hx):
    hx = hx.replace('#', '')
    rgb = []
    for i in range(0, 6, 2):
        rgb.append((int('0x'+hx[i:i+2], 0)+1)*256-1)
    return rgb

def convert_code(display, keycode):
    return display.lookup_string(display.keycode_to_keysym(keycode, 0))

from Xlib import X, display
import subprocess
import sys

class PyMenuGUI:

    BG = "#222222"
    FG = "#ffffff"
    ACTIVE_BG = "#285577"

    PADDING = 5

    active = 0

    displayed = 0

    prompt = ""

    def __init__(self, model):
        self.model = model

        self.disp = display.Display()
        self.screen = self.disp.screen()
        self.root = self.screen.root

        self.width = self.root.get_geometry().width

        colors = self.screen.default_colormap
        fg = colors.alloc_color(*hextorgb(self.FG)).pixel
        bg = colors.alloc_color(*hextorgb(self.BG)).pixel
        bg_active = colors.alloc_color(*hextorgb(self.ACTIVE_BG)).pixel

        self.fg = self.root.create_gc(foreground=fg, subwindow_mode = X.IncludeInferiors)
        self.bg = self.root.create_gc(foreground=bg, subwindow_mode = X.IncludeInferiors)
        self.bg_active = self.root.create_gc(foreground=bg_active, subwindow_mode = X.IncludeInferiors)

        self.draw_bg()

        self.complete()
        self.refill(model.completeCommand('dir'))

        self.disp.sync()

        self.root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

        self.eventloop()


    def precomplete(self, event):
        keycode = event.detail
        key = convert_code(self.disp, keycode)
        #TODO: constants for keycodes
        if keycode == 36: #Enter
            self.disp.ungrab_keyboard(X.CurrentTime)
            self.run()
        elif keycode == 9: #Esc
            self.exit()
        elif keycode == 23: #Tab
            self.prompt = self.model.getCurrent()[self.active]
            self.active = 0
            self.complete()
        elif keycode == 22: #Backspace
            self.prompt = self.prompt[:-1]
            self.complete()
        elif keycode in [114,113]: # Left, Right
            if keycode == 114:
                self.active = (self.active + 1) % self.displayed
            else:
                self.active = max(0, self.active - 1)
            self.refill(self.model.complete(self.prompt))
        else:
            self.prompt += key
            self.complete()


    def eventloop(self):
        while True:
            event = self.root.display.next_event()
            if event.type == X.KeyRelease:
                self.precomplete(event)

    def complete(self):
        self.refill(self.model.complete(self.prompt))

    def exit(self):
        #TODO: Clean screen when exiting
        self.fg.free()
        self.bg.free()
        self.bg_active.free()
        self.disp.sync()
        sys.exit(0)

    def run(self):
        call = self.prompt.split(" ")
        if len(call):
            cmd = call[0]
            path = model.getPath(cmd)
            subprocess.Popen([path]+call[1:])
            self.exit()

    def draw_bg(self):
        #TODO: Draw to canvas instead?
        self.root.fill_rectangle(self.bg, 0,0, self.width,25)
        self.disp.sync()

    def draw_text(self, x, y, text, draw_bg = False):
        extents = self.fg.query_text_extents(text)
        if x+extents.overall_width+2*self.PADDING > self.width:
            return False
        boxWidth = extents.overall_width + 2 * self.PADDING
        boxHeight = extents.font_ascent + 2 * self.PADDING
        if draw_bg:
            self.root.fill_rectangle(self.bg_active, x, 0, boxWidth, boxHeight)
        self.root.draw_text(self.fg, x + self.PADDING, extents.font_ascent + self.PADDING, text)
        return x+boxWidth

    def refill(self, completions):
        i = 0
        self.draw_bg()

        extents = self.fg.query_text_extents(self.prompt)
        x = self.draw_text(0, 0, self.prompt)
        x = max(100, x)
        for completion in completions:
            x = self.draw_text(x, 0, completion, i == self.active)
            if not x:
                self.displayed = i
                break
            i+= 1
        self.disp.sync()

if __name__ == '__main__':
    model = PyMenuCompletions()
    gui   = PyMenuGUI(model)
