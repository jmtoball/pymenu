def hextorgb(hx):
    hx = hx.replace('#', '')
    rgb = []
    for i in range(0, 6, 2):
        rgb.append((int('0x'+hx[i:i+2], 0)+1)*256-1)
    return rgb

def get_level(state):
    active = []
    for exp in reversed(range(0, 12+1)):
        if state == 0:
            break
        if state < 1<<exp:
            continue
        state = state % (1<<exp)
        active.append(exp)
    level = 0
    modjump = False
    for mod in active:
        if mod > 3:
            if modjump:
                continue
            level += mod-3
            modjump = True
        else:
            level += mod+1
    return level

def convert_code(display, keycode, state):
    level = get_level(state)
    keysym = display.keycode_to_keysym(keycode, level)
    if keysym:
        char = display.lookup_string(keysym)
        return char
