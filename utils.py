def hextorgb(hx):
    hx = hx.replace('#', '')
    rgb = []
    for i in range(0, 6, 2):
        rgb.append((int('0x'+hx[i:i+2], 0)+1)*256-1)
    return rgb

# TODO: Check if this works for none-QWERTZ-layouts
def get_level(state):
    active = []
    # The state we get from the keyboard-event is actually a mask
    # Let's see which of its 12 bits are active
    for exp in reversed(range(0, 12+1)):
        if state == 0:
            break
        if state < 1<<exp:
            continue
        state = state % (1<<exp)
        active.append(exp+1)
    level = 0
    modjump = False
    # For those active bits, calculate the level
    # modN-keys are bits > 3. They set a value
    # bits 0-3 increment this value
    # The final level is the key-lookup-level
    for mod in active:
        if mod > 3:
            if modjump:
                continue
            level += mod-4
            modjump = True
        else:
            level += mod
    return level

def sym_to_char(display, keysym):
    if keysym:
        char = display.lookup_string(keysym)
        return char

def code_to_sym(display, keycode, state):
    level = get_level(state)
    return display.keycode_to_keysym(keycode, level)
