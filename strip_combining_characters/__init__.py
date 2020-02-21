# -*- coding: utf-8 -*-
# Version: 1.9
# See github page to report issues or contribute:
# https://github.com/hssm/anki-addons

import unicodedata

from anki.find import Finder
from anki.hooks import wrap
from aqt import *
from aqt.browser import DataModel
from aqt.forms.browser import Ui_Dialog

CONF_KEY_CHECKED = 'strip_comb_checked'


def stripCombining(txt):
    "Return txt with all combining characters removed."
    norm = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in norm if not unicodedata.combining(c)])


def mySearch(self, txt, _old):
    """Perform a search using a custom search function if the stripping
    checkbox is checked."""

    # NOTE: We override the finder function on the click of the browser's
    # "search" button but restore the original version after the search
    # is done since this function is used elsewhere.
    if self.browser.form.scToggleButton.isChecked():
        orig = Finder._findText
        Finder._findText = myFindText
        txt = stripCombining(txt)
        _old(self, txt)
        Finder._findText = orig
        return
    else:
        _old(self, txt)


def myFindText(self, val, args):
    """Build a custom SQL query to invoke a function to strip combining
    characters from the search space."""

    val = val.replace("*", "%")
    args.append("%"+val+"%")
    args.append("%"+val+"%")

    # NOTE: the "?" is user input which is already stripped on search
    return "(n.sfld like ? escape '\\' or "\
        "stripCombining(n.flds) like ? escape '\\')"


def mySetupUi(self, mw):
    """Add new items to the browser UI to allow toggling the add-on."""

    # Create a new SQL function that we can use in our queries.
    mw.col.db._db.create_function("stripCombining", 1, stripCombining)

    # Our UI stuff
    self.scToggleButton = QCheckBox(self.widget)
    self.scToggleLabel = QLabel(" Ignore\nAccents")

    # Restore checked state
    self.scToggleButton.setCheckState(mw.col.conf.get(CONF_KEY_CHECKED, 0))

    # Save state on toggle
    self.scToggleButton.stateChanged.connect(onChecked)

    # Add our items to the right of the search box. We do this by moving
    # every widget out of the gridlayout and into a new list. We simply
    # add our stuff in the new list in the right place before moving them
    # back to gridlayout.
    n_items = self.gridLayout.count()
    items = []
    for i in range(0, n_items):
        item = self.gridLayout.itemAtPosition(0, i).widget()
        items.append(item)
        if item == self.searchEdit:
            items.append(self.scToggleButton)
            items.append(self.scToggleLabel)

    for i, item in enumerate(items):
        self.gridLayout.addWidget(item, 0, i, 1, 1)


def onChecked(state):
    """Save the checked state in Anki's configuration."""
    mw.col.conf[CONF_KEY_CHECKED] = state


Ui_Dialog.setupUi = wrap(Ui_Dialog.setupUi, mySetupUi)
DataModel.search = wrap(DataModel.search, mySearch, "around")
