# This Python file uses the following encoding: utf-8

# Title: FTS Service Toolkit Main File
# Author: Everly Larche - Integrations Specalist
# Rev: 0.0.3
# Date: 2023-11-28

# This souce is not designed to be read by the end user

################################
# Imports and required Modules #
################################

#import rc_icons
from PyQt6 import (
    QtWidgets,
    uic,
    QtCore
)
import platform, logging, sys, datetime, os, json
from src.dbHandler import mongoHandler
from src.pdfGenerator import MakePDF


###########
# Classes #
###########

class myLogger():
    pass

################

class startPopUp():
    def __init__(self):
        self.popUp = uic.loadUi(os.path.join('_internal', 'startWarning.ui'))

    def showpop(self):
        # Executing the popup holds control until the window is closed
        self.popUp.exec()

################

class mainUI():
    # Classwide variables/values
    commitData = []
    _absDIR = os.getcwd()

    # Class Setup
    def __init__(self):
        # Grab all UI elements that may be needed during startup
        self.window = uic.loadUi(os.path.join('_internal', 'mainwindow.ui'))
        self.loadSNWindow = uic.loadUi(os.path.join('_internal', 'loadSNWindow.ui'))
        self.loadSettingsWindow = uic.loadUi(os.path.join('_internal', 'settings.ui'))
        self.commitQueueWindow = uic.loadUi(os.path.join('_internal', 'commitQueue.ui'))
        self.contWindow = uic.loadUi(os.path.join('_internal', 'continue.ui'))
        self.taskCompleteWindow = uic.loadUi(os.path.join('_internal', 'doneTask.ui'))
        self.searchResults = uic.loadUi(os.path.join('_internal', 'searchResults.ui'))

        # Establish button connectors
        self.window.commitTHS.clicked.connect(lambda: self.addToQueue())
        self.window.PushtoDB.clicked.connect(lambda: self.pushToDB())
        self.commitQueueWindow.remove_from_queue.clicked.connect(lambda: self.removeFromQueue(self.commitQueueWindow.list_commit.currentRow()))
        self.loadSNWindow.buttonBox.accepted.connect(lambda: self.searchForEntry(self.loadSNWindow.sn.text()))
        self.searchResults.buttonBox.accepted.connect(lambda: self.loadEntry(self.searchResults.search_list.currentRow()))
        self.searchResults.generate_report.clicked.connect(lambda: self.generatePDFreport(self.searchResults.search_list.currentRow()))

        #Establish toolbar connectors
        self.window.actionSettings.triggered.connect(lambda: self.showFromToolbar(signal=0))
        self.window.actionLoad_SN.triggered.connect(lambda: self.showFromToolbar(signal=1))
        self.window.actionCommit_Queue.triggered.connect(lambda: self.showFromToolbar(signal=2))

        # Other UI Set-up
        self.updateDate()
        self.window.date_of_entry.setText(self.todaysDate+" (Current)")

    ################

    # Class Functions
    def updateDate(self):
        self.todaysDate:str = datetime.datetime.today().strftime("%Y-%m-%d")

    def showUI(self):
        self.window.show()

    # to show ui/windows based on button press mapped to case#
    def showFromToolbar(self, signal):
        match signal:
            case 0:
                self.loadSettingsWindow.exec() #exec function are BLOCKING
            case 1:
                endCode:int = self.loadSNWindow.exec()
            case 2:
                displaySN = []
                for items in self.commitData:
                    displaySN.append(items["destCollection"] + " --> SN:" + items["Serial_Number"])

                print(displaySN)
                self.commitQueueWindow.list_commit.addItems(displaySN)
                self.commitQueueWindow.exec()
                self.commitQueueWindow.list_commit.clear()

    # Det. what to commit depending on tab widget index as case statement
    def addToQueue(self):
        signal:int = self.window.tabWidget.currentIndex()

        # Check if the user is sure, if not, end function do not grab data
        if self.contWindow.exec() == 0: return

        match signal:
            case 0:
                with open(os.path.join(self._absDIR, '_templateStructs', 'fs_template.json'), 'r') as jsonFile:
                            fs_template = json.loads(jsonFile.read())
                with open(os.path.join(self._absDIR, '_templateStructs', 'fs_translation.json'), 'r') as jsonFile:
                            fs_translation = json.loads(jsonFile.read())

                self.getNonItterable(fs_template)
                self.childrenData(children=self.window.fs_scroll_area_contents.children() , template=fs_template, translation=fs_translation, get=True, set=False)

            case 1:
                # Open the template JSON structures and pass it along to the functionn to be changed
                with open(os.path.join(self._absDIR, '_templateStructs', 'ths_template.json'), 'r') as jsonFile:
                            ths_template = json.loads(jsonFile.read())
                with open(os.path.join(self._absDIR, '_templateStructs', 'ths_translation.json'), 'r') as jsonFile:
                            ths_translation = json.loads(jsonFile.read())

                self.getNonItterable(ths_template)
                self.childrenData(children=self.window.THS_scroll_area_contents.children(), template=ths_template, translation=ths_translation, get=True, set=False)

            case _:
                pass

        # Clear the fields that have already been read by the ths_template
        self.window.ns_rma.setText("RMA")
        self.window.ns_customer_entry.clear()
        self.window.ns_so.setText("SO")
        self.window.jira_ticket_entry.setText("CST-")
        self.window.svcComments.clear()
        self.window.tech.clear()
        self.window.ths_module_fw.setText("15")

        # Preform other tasks when adding to the queue
        self.window.PushtoDB.setEnabled(True)
        self.updateDate()
        self.taskCompleteWindow.exec()

    def getNonItterable(self, template):
        # Get common/non-itterable elements
        template["Date_of_Entry"] = self.todaysDate
        template["SVC_Details"]["NS_RMA"] = self.window.ns_rma.text()
        template["SVC_Details"]["NS_Customer"] = self.window.ns_customer_entry.text()
        template["SVC_Details"]["NS_Parts_SO"] = self.window.ns_so.text()
        template["SVC_Details"]["Jira_Ticket"] = self.window.jira_ticket_entry.text()
        template["SVC_Details"]["Service_Comments"] = self.window.svcComments.toPlainText()
        template["SVC_Details"]["Warranty_Status"] = self.window.warranty_status.currentText()
        template["SVC_Details"]["Tech"] = self.window.tech.text()
        return template

    def childrenData(self, children, template, translation, get:bool, set:bool):
        if get: entry:dict = template

        for child in children:
            if type(child).__name__ == "QComboBox":
                if get: self.nestedData(entry, translation[child.objectName()], child.currentText(), not get, not set), child.setCurrentIndex(0)
                elif set: child.setCurrentIndex(child.findText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set)))
            elif type(child).__name__ == "QCheckBox":
                if get: self.nestedData(entry, translation[child.objectName()], child.isChecked(), not get, not set), child.setChecked(False)
                elif set: child.setChecked(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set))
            elif type(child).__name__ == "QLineEdit":
                if get: self.nestedData(entry, translation[child.objectName()], child.text(), not get, not set), child.clear()
                elif set: child.setText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set))
            elif type(child).__name__ == "QPlainTextEdit":
                if get: self.nestedData(entry, translation[child.objectName()], child.toPlainText(), not get, not set), child.clear()
                elif set: child.setPlainText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set))
            else:
                pass

        if get: self.commitData.append(entry)

    def nestedData(self, target, targetKey, value, get:bool, set:bool):
        for k in target.keys():
            if targetKey == k:
                if set:
                    target[k] = value
                    return target
                elif get:
                    value = target[k]
                    break
            elif isinstance(target[k], dict):
                value = self.nestedData(target[k], targetKey, value, get, set)
                if (value != None) and (get): return value
        return value

    def pushToDB(self):
        # Check if the user is sure, if not, end function do not grab data
        if self.contWindow.exec() == 0: return

        db = mongoHandler()
        print(db.pushCollection(self.commitData))
        # Need to clear queue after commit and disable push to db button
        self.commitData = []
        self.window.PushtoDB.setEnabled(False)
        self.commitQueueWindow.list_commit.clear()
        self.taskCompleteWindow.exec()

    def removeFromQueue(self, index:int):
        print(index)
        self.commitQueueWindow.list_commit.takeItem(index)
        if len(self.commitData) > 0: self.commitData.pop(index)
        print(self.commitData)
        if len(self.commitData) <= 0: self.window.PushtoDB.setEnabled(False)

    def searchForEntry(self, serialNumber:str):
        print(serialNumber)
        db = mongoHandler()
        self.dbData = []
        self.dbData = db.getCollection(serialNumber)
        displaySN = []
        for entry in self.dbData:
            displaySN.append(entry["destCollection"] + " --> SN:" + entry["Serial_Number"] + f"  [{entry['Date_of_Entry']}]")
        self.searchResults.label.setText(f"{len(displaySN)} Results Found:")
        self.searchResults.search_list.addItems(displaySN)
        self.searchResults.exec()
        self.searchResults.search_list.clear()

    def loadEntry(self, index:int):
        # Check if the user is sure, if not, end function do not grab data
        if self.contWindow.exec() == 0: return

        # Clear out all other entries from mem. apart from the one we want to load
        self.dbData = self.dbData[index]
        type:str = self.dbData["destCollection"]
        match type:
            case "FS":
                self.window.tabWidget.setCurrentIndex(0)
                with open(os.path.join(self._absDIR, '_templateStructs', 'fs_translation.json'), 'r') as jsonFile:
                            fs_translation = json.loads(jsonFile.read())
                self.childrenData(children=self.window.fs_scroll_area_contents.children(), template=None, translation=fs_translation, get=False, set=True)

            case "THS":
                self.window.tabWidget.setCurrentIndex(1)
                # Open the template JSON structures and pass it along to the functionn to be changed
                with open(os.path.join(self._absDIR, '_templateStructs', 'ths_translation.json'), 'r') as jsonFile:
                            ths_translation = json.loads(jsonFile.read())
                self.childrenData(children=self.window.THS_scroll_area_contents.children(), template=None, translation=ths_translation, get=False, set=True)

        self.window.ns_rma.setText(self.dbData["SVC_Details"]["NS_RMA"])
        self.window.ns_customer_entry.setText(self.dbData["SVC_Details"]["NS_Customer"])
        self.window.ns_so.setText(self.dbData["SVC_Details"]["NS_Parts_SO"])
        self.window.jira_ticket_entry.setText(self.dbData["SVC_Details"]["Jira_Ticket"])
        self.window.svcComments.setText(self.dbData["SVC_Details"]["Service_Comments"])
        self.window.tech.setText(self.dbData["SVC_Details"]["Tech"])
        self.window.ths_module_fw.setText(self.dbData["SVC_Details"]["Incoming_and_Visual"]["00-THS-3_FW_Ver"])

        # Use the method for getting/setting child data and fill in fields
        # Manually fill in the non-itterable fields

    def generatePDFreport(self, index:int):
        # Show a window that the report is being generated
        data = self.dbData[index]
        generator = MakePDF()
        rc = generator.render(data["destCollection"], data, self.todaysDate)
        print(rc)



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
