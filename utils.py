def hextorgb(hx):
    hx = hx.replace('#', '')
    rgb = []
    for i in range(0, 6, 2):
        rgb.append((int('0x'+hx[i:i+2], 0)+1)*256-1)
    return rgb

def convert_code(display, keycode):
    return display.lookup_string(display.keycode_to_keysym(keycode, 0))
