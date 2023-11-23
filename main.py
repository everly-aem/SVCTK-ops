# This Python file uses the following encoding: utf-8

# Title: FTS Service Toolkit Main File
# Author: Everly Larche - Integrations Specalist
# Rev: NR - WIP
# Date: 2023-11-03

# This souce is not designed to be read by the end user

################################
# Imports and required Modules #
################################

#import rc_icons
from PyQt6 import (
    QtWidgets,
    uic
)
import platform, logging, sys, datetime
#import dbHandler


###########
# Classes #
###########

class myLogger():
    pass

################

class startPopUp():
    def __init__(self):
        self.popUp = uic.loadUi("startWarning.ui")

    def showpop(self):
        # Executing the popup holds control until the window is closed
        self.popUp.exec()

################

class mainUI():
    # Classwide variables/values
    commitData = []

    todaysDate:str = datetime.datetime.today().strftime("%Y-%m-%d")


    # Class Setup
    def __init__(self):
        # Grab all UI elements that may be needed during startup
        self.window = uic.loadUi("mainwindow.ui")
        self.loadSNWindow = uic.loadUi("loadSNWindow.ui")
        self.loadSettingsWindow = uic.loadUi("settings.ui")
        self.commitQueueWindow = uic.loadUi("commitQueue.ui")
        #self.contWindow = uic.loadUi("continue.ui")

        # Establish button connectors
        self.window.commitTHS.clicked.connect(lambda: self.commitDB())

        #Establish toolbar connectors
        self.window.actionSettings.triggered.connect(lambda: self.showFromToolbar(signal=0))
        self.window.actionLoad_SN.triggered.connect(lambda: self.showFromToolbar(signal=1))
        self.window.actionCommit_Queue.triggered.connect(lambda: self.showFromToolbar(signal=2))

        # Other UI Set-up
        self.window.date_of_entry.setText(self.todaysDate+" (Current)")

    ################

    # Class Functions
    def showUI(self):
        self.window.show()

    # to show ui/windows based on button press mapped to case#
    def showFromToolbar(self, signal):
        match signal:
            case 0:
                self.loadSettingsWindow.exec() #exec function are BLOCKING
            case 1:
                endCode:int = self.loadSNWindow.exec() # Depending on user selection, return code will change
                # how do I get the field data from the window before it closes?
                if endCode == 1: self.window.svcComments.setPlainText("I put some text in here!") #toPlainText and setPlainText
                print(f"From the widget: {self.window.svcComments.toPlainText()}")
                # How to grab data from window UI before destruction??
            case 2:
                displaySN = []
                for items in self.commitData:
                    displaySN.append(items["destCollection"] + " --> SN:" + items["Serial_Number"])

                print(displaySN)
                self.commitQueueWindow.list_commit.addItems(displaySN)
                self.commitQueueWindow.exec()

    # Det. what to commit and commit to DB
    def commitDB(self):
        signal:int = self.window.tabWidget.currentIndex()

        # Check if the user is sure, if not, end function do not grab data
        #if self.contWindow.exec() == 0: return

        match signal:
            case 0:
                print(f"Commit FS Pressed! {signal}")
                # Gather data from each child element using a ref dict with value and type
                #print(self.window.tabWidget.children())
            case 1:
                ths_template = {
                "destCollection": "THS",
                  "Serial_Number": 123456,
                  "Date_of_Entry": self.todaysDate,
                  "SVC_Details": {
                    "NS_RMA": 4535,
                    "NS_Customer": "FTS",
                    "NS_Parts_SO": "SO35623",
                    "Jira_Tiket": "CST-532",
                    "THS_Sensor_Info": {
                      "00-THS-3_Serial_Number": 987654,
                      "Incoming_Status": "Preventative Maintenance"
                    },
                    "Incoming_and_Visual": {
                      "Passed_Checks": "Passed",
                      "00-THS-3_FW_Ver": 15,
                      "Visual_Complete": False,
                      "Cleaned": False
                    },
                    "Calibration_and_Servicing": {
                      "Icoming_RH": "Pass",
                      "Incoming_Temp": "Pass",
                      "Required_Repairs": False,
                      "RH_Calibrated": False,
                      "Builentins_Used": False,
                      "Active_Current_Pass": False,
                      "Filter_Replaced": False,
                      "Desiccant_Replaced": False,
                      "RH_Calibration_Pass": False,
                      "Temp_Calibration_Pass": False,
                      "CTM_Installed": False
                    },
                    "Service_Comments": "Long String of comments here",
                    "Warranty_Status": "Limited Warranty",
                    "Tech": "Everly Larche"
                  }
                }

                ths_translation = {
                    "ths_sn":"Serial_Number",
                    "ths_module_sn":"00-THS-3_Serial_Number",
                    "ths_incoming_status":"Incoming_Status",
                    "ths_initial_verification":"Passed_Checks",
                    "ths_module_fw":"00-THS-3_FW_Ver",
                    "ths_visual":"Visual_Complete",
                    "ths_cleaning":"Cleaned",
                    "ths_incoming_rh":"Incoming_RH",
                    "ths_incoming_temp":"Incoming_Temp",
                    "ths_repairs_required":"Required_Repairs",
                    "ths_rh_calibration":"RH_Calibrated",
                    "ths_builentins_used":"Builentins_Used",
                    "ths_active_current":"Active_Current_Pass",
                    "ths_filter":"Filter_Replaced",
                    "ths_desiccant":"Desciccant_Replaced",
                    "ths_rh_calibration_pass":"RH_Calibration_Pass",
                    "ths_temp_calibration":"Temp_calibration_Pass",
                    "ths_ctm":"CTM_Installed"
                }

                self.getChildrenData(children=self.window.THS_scroll_area_contents.children(), template=ths_template, translation=ths_translation)
            case _:
                pass

    def getChildrenData(self, children, template, translation):
        entry = template

        for child in children:
            if type(child).__name__ == "QComboBox":
                entry.update({translation[child.objectName()]:child.currentText()})
            elif type(child).__name__ == "QCheckBox":
                entry.update({translation[child.objectName()]:child.isChecked()})
            elif type(child).__name__ == "QLineEdit":
                entry.update({translation[child.objectName()]:child.text()})
            else:
                pass

        print(entry)
        self.commitData.append(entry)





#############
# Main Loop #
#############

# Application can not be called as a deamon or child of another application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if platform.system() == "Windows": app.setStyle("Fusion")

    #Load UI(s)
    ui = mainUI()
    pop = startPopUp()

    # Show in order the UI windows
    pop.showpop()
    ui.showUI()
    app.exec()
