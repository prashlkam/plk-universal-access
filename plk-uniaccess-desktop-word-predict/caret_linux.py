# Linux caret fetching: try AT-SPI via pyatspi, fallback to xdotool geometry.
import subprocess, shutil
def get_caret_position():
    # Try AT-SPI (pyatspi) first for accurate caret extents
    try:
        import pyatspi
        desktop = pyatspi.Registry.getDesktop(0)
        # find focused application and text interface - this is a simplified attempt
        for i in range(desktop.childCount):
            app = desktop.getChildAtIndex(i)
            if app.getState().contains(pyatspi.STATE_ACTIVE):
                for j in range(app.childCount):
                    c = app.getChildAtIndex(j)
                    if c.getRoleName() in ('text', 'entry', 'editable text'):
                        try:
                            iface = c.queryText()
                            (start, end) = iface.getCaretOffset()
                            extents = iface.getCharacterExtents(start, pyatspi.DESKTOP_COORD_TYPE_SCREEN)
                            return (int(extents.x), int(extents.y + extents.height))
                        except Exception:
                            continue
    except Exception:
        pass
    # Fallback: xdotool to get active window geometry and approximate caret
    try:
        if shutil.which('xdotool') is None:
            return None
        wid = subprocess.check_output(['xdotool', 'getactivewindow']).strip()
        geom = subprocess.check_output(['xdotool', 'getwindowgeometry', '--shell', wid]).decode()
        geomd = dict(line.split('=') for line in geom.strip().splitlines())
        x, y, h = int(geomd.get('X',0)), int(geomd.get('Y',0)), int(geomd.get('HEIGHT',0))
        # crude approximation: return some offset inside window
        return (x + 50, y + 50)
    except Exception:
        return None
