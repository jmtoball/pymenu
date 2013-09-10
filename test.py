from Xlib import X, display

def hextorgb(hx):
    hx = hx.replace('#', '')
    rgb = []
    for i in range(0, 6, 2):
        rgb.append((int('0x'+hx[i:i+2], 0)+1)*256-1)
    return rgb

def convert_code(display, keycode):
    return display.lookup_string(display.keycode_to_keysym(keycode, 0))

disp = display.Display()
screen = disp.screen()
root = screen.root
width = root.get_geometry().width
colors = screen.default_colormap
bg1 = colors.alloc_color(34*256, 34*256, 34*256).pixel
bg2 = colors.alloc_color(40*256, 85*256, 19*256).pixel
fg = colors.alloc_color(256**2-1, 256**2-1, 256**2-1).pixel
gc = root.create_gc(subwindow_mode = X.IncludeInferiors)

gc.change(foreground = bg1)
root.fill_rectangle(gc, 0,0, width,25)

extents =  gc.query_text_extents("lol")

gc.change(foreground = bg2)
root.fill_rectangle(gc, 0,0, extents.overall_width+10, extents.overall_ascent+10)

gc.change(foreground = fg)
root.draw_text(gc, 5, extents.overall_ascent+5, "lol")
disp.sync()

root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

while True:
    event = root.display.next_event()
    if event.type == X.KeyRelease:
        print str(convert_code(disp, event.detail))
        disp.ungrab_keyboard(X.CurrentTime)
