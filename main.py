# This Python file uses the following encoding: utf-8

# Title: FTS Service Toolkit Main File
# Author: Everly Larche - Integrations Specalist
# Rev: NR
# Date: 2023-10-03

################################
# Imports and required Modules #
################################

import sys
#import rc_icons
from PyQt6 import QtWidgets, uic



###########
# Classes #
###########

class startPopUp():
    def __init__(self):
        self.popUp = uic.loadUi("startWarning.ui")

    def showpop(self):
        # Executing the popup holds control until the window is closed
        self.popUp.exec()

################

class mainUI():
    def __init__(self):
        # Grab all UI elements that may be needed during startup
        self.window = uic.loadUi("mainwindow.ui")
        self.loadSNWindow = uic.loadUi("loadSNWindow.ui")
        self.loadSettingsWindow = uic.loadUi("settings.ui")

        # Establish button connectors
        self.window.commitTHS.clicked.connect(lambda: self.commitDB(signal=0))

        #Establish toolbar connectors
        self.window.actionSettings.triggered.connect(lambda: self.showFromToolbar(signal=0))
        self.window.actionLoad_SN.triggered.connect(lambda: self.showFromToolbar(signal=1))


    def showUI(self):
        self.window.show()

    # to show ui/windows based on button press mapped to case#
    def showFromToolbar(self, signal):
        match signal:
            case 0:
                self.loadSettingsWindow.exec()
            case 1:
                self.loadSNWindow.exec()

    # Det. what to commit and commit to DB
    def commitDB(self, signal):
        match signal:
            case 0:
                print(f"commitTHS Pressed! {signal}")
            case _:
                pass




#############
# Main Loop #
#############

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    #Load UI(s)
    ui = mainUI()
    pop = startPopUp()

    # Show in order the UI windows
    pop.showpop()
    ui.showUI()
    app.exec()
