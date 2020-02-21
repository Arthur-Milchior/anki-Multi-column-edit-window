import sys

from aqt import mw
from aqt.utils import showWarning

# end configuration

userOption = None


def _getUserOption():
    global userOption
    if userOption is None:
        userOption = mw.addonManager.getConfig(__name__)
        transferConfig()


def getUserOption(key=None, default=None):
    """Get the user option if it is set. Otherwise return the default
    value and add it to the config.

    When an add-on was updated, new config key were not added. This
    was a problem because user never discover those configs. By adding
    it to the config file, users will see the option and can configure it.

    """
    _getUserOption()
    if key is None:
        return userOption
    if key in userOption:
        return userOption[key]
    else:
        userOption[key] = default
        writeConfig()
        return default


def writeConfig():
    mw.addonManager.writeConfig(__name__, userOption)


def update(_):
    global userOption, fromName
    userOption = None
    fromName = None


mw.addonManager.setConfigUpdatedAction(__name__, update)

fromName = None


def getFromName(name):
    global fromName
    if fromName is None:
        fromName = dict()
        for dic in getUserOption("columns"):
            fromName[dic["name"]] = dic
    return fromName.get(name)


def setUserOption(key, value):
    _getUserOption()
    userOption[key] = value
    writeConfig()


###############################################
#The code below should be eventually be deleted. It is used only to transfer the old configuration to the new one#
###############################################
CONF_KEY_COLUMN_COUNT = 'multi_column_count'


def transferConfig():
    if not getUserOption("transfer done", False):
        for key, value in mw.pm.profile.items():
            if CONF_KEY_COLUMN_COUNT in key:
                key = key.replace(f"{CONF_KEY_COLUMN_COUNT}-", "")
                setUserOption(key, value)
        setUserOption("transfer done", True)
