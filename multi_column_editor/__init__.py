# -*- coding: utf-8 -*-
# Version: 2.5
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

import aqt.editor
from anki.hooks import wrap
from aqt import *
from aqt.editor import Editor
from .from_file import str_from_file_name

from .config import getUserOption, setUserOption

# A sensible maximum number of columns we are able to set

# Flag to enable hack to make Frozen Fields look normal
ffFix = False

aqt.editor._html += f"""
<script>
{str_from_file_name("js.js")}
</script>
"""


def getKeyForContext(self, field=None):
    """Get a key that takes into account the parent window type and
    the note type.

    This allows us to have a different key for different contexts,
    since we may want different column counts in the browser vs
    note adder, or for different note types.
    """
    key = str(self.note.mid)
    if getUserOption("same config for each window", False):
        key = f"{self.parentWindow.__class__.__name__}-{key}"
    if field is not None:
        key = f"{key}{field}"
    return key


def onColumnCountChanged(self, count):
    "Save column count to settings and re-draw with new count."
    setUserOption(getKeyForContext(self), count)


def myEditorInit(self, mw, widget, parentWindow, addMode=False):
    self.ccSpin = QSpinBox(self.widget)
    b = QPushButton(u"▾")
    b.clicked.connect(lambda: onConfigClick(self))
    b.setFixedHeight(self.tags.height())
    b.setFixedWidth(25)
    b.setAutoDefault(False)
    hbox = QHBoxLayout()
    hbox.setSpacing(0)
    label = QLabel("Columns:", self.widget)
    hbox.addWidget(label)
    hbox.addWidget(self.ccSpin)
    hbox.addWidget(b)

    self.ccSpin.setMinimum(1)
    self.ccSpin.setMaximum(getUserOption("MAX_COLUMNS"))
    self.ccSpin.valueChanged.connect(
        lambda value: onColumnCountChanged(self, value))

    # We will place the column count editor next to the tags widget.
    pLayout = self.tags.parentWidget().layout()
    # Get the indices of the tags widget
    (rIdx, cIdx, r, c) = pLayout.getItemPosition(pLayout.indexOf(self.tags))
    # Place ours on the same row, to its right.
    pLayout.addLayout(hbox, rIdx, cIdx+1)

    # If the user has the Frozen Fields add-on installed, tweak the
    # layout a bit to make it look right.
    global ffFix
    try:
        __import__("Frozen Fields")
        ffFix = True
    except:
        pass


def myOnBridgeCmd(self, cmd):
    """
    Called from JavaScript to inject some values before it needs
    them.
    """
    if cmd == "mceTrigger":
        count = getUserOption(getKeyForContext(self), 1)
        self.web.eval(f"setColumnCount({count});")
        self.ccSpin.blockSignals(True)
        self.ccSpin.setValue(count)
        self.ccSpin.blockSignals(False)
        for fld, val in self.note.items():
            key = getKeyForContext(self, field=fld)
            if getUserOption(key, False):
                self.web.eval(f"setSingleLine('{fld}');")
        if ffFix:
            self.web.eval("setFFFix(true)")
        self.web.eval("makeColumns2()")


def onConfigClick(self):
    m = QMenu(self.mw)

    def addCheckableAction(menu, key, text):
        a = menu.addAction(text)
        a.setCheckable(True)
        a.setChecked(getUserOption(key, False))
        a.toggled.connect(lambda b, k=key: onCheck(self, k))

    # Descriptive title thing
    a = QAction(u"―Single Row―", m)
    a.setEnabled(False)
    m.addAction(a)

    for fld, val in self.note.items():
        key = getKeyForContext(self, field=fld)
        addCheckableAction(m, key, fld)

    m.exec_(QCursor.pos())


def onCheck(self, key):
    setUserOption(key, not getUserOption(key))


Editor.__init__ = wrap(Editor.__init__, myEditorInit)
Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, myOnBridgeCmd, 'before')
