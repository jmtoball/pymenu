from Xlib import X, display
import subprocess
import sys

from completer import PyMenuCompletions
from utils import hextorgb, convert_code

class KeyCodes:

    Backspace = 22
    Enter     = 36
    Esc       = 9
    Left      = 113
    Right     = 114
    Space     = 65
    Tab       = 23

class PyMenuGUI:

    BG = "#222222"
    FG = "#ffffff"
    ACTIVE_BG = "#285577"

    PADDING = 5

    active = 0

    step = 0

    displayed = 0

    prompt = ""

    def __init__(self, model):
        self.model = model

        self.disp = display.Display()
        self.screen = self.disp.screen()
        self.root = self.screen.root

        self.width = self.root.get_geometry().width

        self.canvas = self.root.create_window(0,0,self.width, 30, 0, self.screen.root_depth, X.CopyFromParent, 0)
        self.canvas.change_attributes(override_redirect=True)
        self.canvas.map()

        colors = self.screen.default_colormap
        fg = colors.alloc_color(*hextorgb(self.FG)).pixel
        bg = colors.alloc_color(*hextorgb(self.BG)).pixel
        bg_active = colors.alloc_color(*hextorgb(self.ACTIVE_BG)).pixel

        self.fg = self.canvas.create_gc(foreground=fg, subwindow_mode = X.IncludeInferiors)
        self.bg = self.canvas.create_gc(foreground=bg, subwindow_mode = X.IncludeInferiors)
        self.bg_active = self.canvas.create_gc(foreground=bg_active, subwindow_mode = X.IncludeInferiors)

        self.draw_bg()

        self.complete()
        self.refill(self.model.completeCommand('dir'))

        self.disp.sync()

        self.root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

        self.eventloop()

    def precomplete(self, event):
        keycode = event.detail
        key = convert_code(self.disp, keycode)
        if keycode == KeyCodes.Enter:
            self.setPrompt(self.model.getCurrent()[self.active])
            self.run()
        elif keycode == KeyCodes.Esc:
            self.exit()
        elif keycode == KeyCodes.Space:
            self.setPrompt(self.model.getCurrent()[self.active]+" ")
            self.active = 0
            self.step += 1
        elif keycode == KeyCodes.Tab:
            self.setPrompt(self.model.getCurrent()[self.active]+" ")
            self.active = 0
            self.step += 1
            self.complete()
        elif keycode == KeyCodes.Backspace:
            self.setPrompt(self.getPrompt()[:-1])
            self.complete()
        elif keycode in [KeyCodes.Left, KeyCodes.Right]:
            if keycode == KeyCodes.Right:
                self.active = (self.active + 1) % self.displayed
            else:
                self.active = max(0, self.active - 1)
            self.refill(self.model.complete(self.prompt))
        elif key:
            self.setPrompt(self.getPrompt()+key)
            self.complete()

    def eventloop(self):
        while True:
            event = self.root.display.next_event()
            if event.type == X.KeyRelease:
                self.precomplete(event)

    def setPrompt(self, text, full=False):
        if full:
            self.prompt = text
        else:
            tokens = self.getPrompt(full=True).split(" ")
            tokens[self.step] = text
            self.prompt = " ".join(tokens)

    def getPrompt(self, full=False):
        if full:
            return self.prompt
        else:
            return self.prompt.split(" ")[self.step]

    def complete(self):
        if self.step >= 1:
            mode = PyMenuCompletions.COMPLETE_PATH
        else:
            mode = PyMenuCompletions.COMPLETE_CMD
        completions = self.model.complete(self.getPrompt(), mode=mode)
        self.refill(completions)

    def exit(self):
        #TODO: Clean screen when exiting
        self.disp.ungrab_keyboard(X.CurrentTime)
        self.fg.free()
        self.bg.free()
        self.bg_active.free()
        self.canvas.destroy()
        self.disp.sync()
        self.disp.close()
        sys.exit(0)

    def run(self):
        call = self.prompt.split(" ")
        if len(call):
            cmd = call[0]
            print call
            path = self.model.getPath(cmd)
            subprocess.Popen([path]+call[1:])
            self.exit()

    def draw_bg(self):
        #TODO: Draw to canvas instead?
        self.canvas.fill_rectangle(self.bg, 0,0, self.width,25)
        self.disp.sync()

    def draw_text(self, x, y, text, draw_bg = False):
        extents = self.fg.query_text_extents(text)
        if x+extents.overall_width+2*self.PADDING > self.width:
            return False
        boxWidth = extents.overall_width + 2 * self.PADDING
        boxHeight = extents.font_ascent + 2 * self.PADDING
        if draw_bg:
            self.canvas.fill_rectangle(self.bg_active, x, 0, boxWidth, boxHeight)
        self.canvas.draw_text(self.fg, x + self.PADDING, extents.font_ascent + self.PADDING, text)
        return x+boxWidth

    def refill(self, completions):
        i = 0
        self.draw_bg()

        extents = self.fg.query_text_extents(self.getPrompt(full=True))
        x = self.draw_text(0, 0, self.getPrompt(full=True))
        x = max(100, x)
        for completion in completions:
            x = self.draw_text(x, 0, completion, i == self.active)
            if not x:
                self.displayed = i
                break
            i+= 1
        self.disp.sync()
