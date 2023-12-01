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
    QtCore,
    QtGui
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
    def __init__(self, appREF:QtWidgets.QApplication):
        with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json')) as file:
            config = json.loads(file.read())

        # Grab all UI elements that may be needed during startup
        self.window = uic.loadUi(os.path.join('_internal', 'mainwindow.ui'))
        self.loadSNWindow = uic.loadUi(os.path.join('_internal', 'loadSNWindow.ui'))
        self.loadSettingsWindow = uic.loadUi(os.path.join('_internal', 'settings.ui'))
        self.commitQueueWindow = uic.loadUi(os.path.join('_internal', 'commitQueue.ui'))
        self.contWindow = uic.loadUi(os.path.join('_internal', 'continue.ui'))
        self.taskCompleteWindow = uic.loadUi(os.path.join('_internal', 'doneTask.ui'))
        self.searchResults = uic.loadUi(os.path.join('_internal', 'searchResults.ui'))
        self.about = uic.loadUi(os.path.join(self._absDIR, '_internal', 'about.ui'))
        self.error = uic.loadUi(os.path.join(self._absDIR, '_internal', 'taskError.ui'))

        # Establish button connectors
        self.window.commitTHS.clicked.connect(lambda: self.addToQueue())
        self.window.PushtoDB.clicked.connect(lambda: self.pushToDB())
        self.commitQueueWindow.remove_from_queue.clicked.connect(lambda: self.removeFromQueue(self.commitQueueWindow.list_commit.currentRow()))
        self.loadSNWindow.buttonBox.accepted.connect(lambda: self.searchForEntry(self.loadSNWindow.sn.text()))
        self.searchResults.buttonBox.accepted.connect(lambda: self.loadEntry(self.searchResults.search_list.currentRow()))
        self.searchResults.generate_report.clicked.connect(lambda: self.generatePDFreport(self.searchResults.search_list.currentRow()))
        self.loadSettingsWindow.save_settings.clicked.connect(lambda: self.loadSettings(True))
        self.window.clear_all_fields.clicked.connect(lambda: self.clearFields(True, True))

        #Establish toolbar connectors
        self.window.actionSettings.triggered.connect(lambda: self.loadSettings(False))
        self.window.actionLoad_SN.triggered.connect(lambda: self.loadSNWindow.exec())
        self.window.actionCommit_Queue.triggered.connect(lambda: self.showFromToolbar(signal=2))
        self.window.actionClear_Fields.triggered.connect(lambda: self.clearFields(True, True))
        self.window.actionAbout.triggered.connect(lambda: self.about.exec())

        # Other UI Set-up
        self.updateDate()
        self.window.date_of_entry.setText(self.todaysDate+" (Current)")
        self.app = appREF
        self.window.tech.setText(config["APP_PREF"]["app_tech"])
        self.window.tabWidget.setCurrentIndex(config["APP_PREF"]["app_start_tab"])

        self.setupDataValidators()

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
                self.loadSNWindow.exec()
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
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'fs_template.json'), 'r') as jsonFile:
                            fs_template = json.loads(jsonFile.read())
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'fs_translation.json'), 'r') as jsonFile:
                            fs_translation = json.loads(jsonFile.read())

                self.getNonItterable(fs_template)
                self.childrenData(children=self.window.fs_scroll_area_contents.children() , template=fs_template, translation=fs_translation, get=True, set=False)

            case 1:
                # Open the template JSON structures and pass it along to the functionn to be changed
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'ths_template.json'), 'r') as jsonFile:
                            ths_template = json.loads(jsonFile.read())
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'ths_translation.json'), 'r') as jsonFile:
                            ths_translation = json.loads(jsonFile.read())

                self.getNonItterable(ths_template)
                self.childrenData(children=self.window.THS_scroll_area_contents.children(), template=ths_template, translation=ths_translation, get=True, set=False)

            case _:
                pass

        # Clear the fields that have already been read by the ths_template
        self.clearFields(False, True)

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
                elif set: child.setCurrentIndex(child.findText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set))), child.setEnabled(False)
            elif type(child).__name__ == "QCheckBox":
                if get: self.nestedData(entry, translation[child.objectName()], child.isChecked(), not get, not set), child.setChecked(False)
                elif set: child.setChecked(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set)), child.setEnabled(False)
            elif type(child).__name__ == "QLineEdit":
                if get: self.nestedData(entry, translation[child.objectName()], child.text(), not get, not set), child.clear()
                elif set: child.setText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set)), child.setEnabled(False)
            elif type(child).__name__ == "QPlainTextEdit":
                if get: self.nestedData(entry, translation[child.objectName()], child.toPlainText(), not get, not set), child.clear()
                elif set: child.setPlainText(self.nestedData(self.dbData, translation[child.objectName()], None, not get, not set)), child.setEnabled(False)
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

        try:
            self.dbData = db.getCollection(serialNumber)
        except Exception as e:
            self.error.title.setText(str(type(e).__name__))
            self.error.message.setText(str(e))
            self.error.exec()
            return

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
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'fs_translation.json'), 'r') as jsonFile:
                            fs_translation = json.loads(jsonFile.read())
                self.childrenData(children=self.window.fs_scroll_area_contents.children(), template=None, translation=fs_translation, get=False, set=True)

            case "THS":
                self.window.tabWidget.setCurrentIndex(1)
                # Open the template JSON structures and pass it along to the functionn to be changed
                with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'ths_translation.json'), 'r') as jsonFile:
                            ths_translation = json.loads(jsonFile.read())
                self.childrenData(children=self.window.THS_scroll_area_contents.children(), template=None, translation=ths_translation, get=False, set=True)

        self.window.ns_rma.setText(self.dbData["SVC_Details"]["NS_RMA"])
        self.window.ns_rma.setEnabled(False)
        self.window.ns_customer_entry.setText(self.dbData["SVC_Details"]["NS_Customer"])
        self.window.ns_customer_entry.setEnabled(False)
        self.window.ns_so.setText(self.dbData["SVC_Details"]["NS_Parts_SO"])
        self.window.ns_so.setEnabled(False)
        self.window.jira_ticket_entry.setText(self.dbData["SVC_Details"]["Jira_Ticket"])
        self.window.jira_ticket_entry.setEnabled(False)
        self.window.svcComments.setText(self.dbData["SVC_Details"]["Service_Comments"])
        self.window.svcComments.setEnabled(False)
        self.window.tech.setText(self.dbData["SVC_Details"]["Tech"])
        self.window.tech.setEnabled(False)
        self.window.ths_module_fw.setText(self.dbData["SVC_Details"]["Incoming_and_Visual"]["00-THS-3_FW_Ver"])
        self.window.ths_module_fw.setEnabled(False)

        # Use the method for getting/setting child data and fill in fields
        # Manually fill in the non-itterable fields

    def generatePDFreport(self, index:int):
        self.showBusy(True)
        data = self.dbData[index]
        generator = MakePDF()
        rc = generator.render(data["destCollection"], data, self.todaysDate)
        self.showBusy(False)
        if rc == 0: self.showCompleteWindow("Generate PDF Complete!", "Genderated PDF file was created and saved to your output foler.")

    def showCompleteWindow(self, task:str, message:str):
        self.taskCompleteWindow.title.setText(task)
        self.taskCompleteWindow.message.setText(message)
        self.taskCompleteWindow.exec()

    def showBusy(self, TF:bool):
        try:
            if TF: app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        finally:
            app.restoreOverrideCursor()

    def loadSettings(self, set:bool):
        with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json'), 'r') as configFile:
            config = json.loads(configFile.read())

        # Unpact only the required items from the configuration file as smaller dicts
        SETTING:dict = {**config["DB"], **config["APP_PREF"], **config["PDF_PREF"]}

        # Set up whats needed in the UI based on the settings avaliable (ex. the collections being used)
        widgets = self.layoutWidgets(self.loadSettingsWindow.settingsLayout)
        for widget in widgets.keys():
            print(widget.objectName())
            if widget.objectName() in SETTING:
                # widgets[widget] returns the widgets TYPE as str
                match widgets[widget]:
                    case 'QLineEdit':
                        if set: SETTING[widget.objectName()] = widget.text()
                        else: widget.setText(SETTING[widget.objectName()])

                    case 'QComboBox':
                        if set: pass
                        else: widget.setCurrentIndex(SETTING[widget.objectName()])

                    case 'QListWidget':
                        for item in SETTING[widget.objectName()]:
                            if set: pass
                            else: widget.addItem(item)

                    case _:
                        pass

        if set:
            for key in SETTING.keys():
                self.nestedData(config, key, SETTING[key], False, True)
            print(config)
            jsonString = json.dumps(config, indent=6)
            print(jsonString)
            with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json'), 'w') as configFile:
                configFile.write(jsonString)

            self.showCompleteWindow("Settings Saved!", "Some settings may not apply until the application is restarted.")

        else: self.loadSettingsWindow.exec()

    def layoutWidgets(self, layout):
        # Empty dict to store all the elements in
        uiElements = {}

        # For each item in the layout (up to the max in the layout), get the name of the widget and its type(class), append it to the dict and return
        for i in range(layout.count()):
            if type(layout.itemAt(i)).__name__ == 'QWidgetItem':
                uiElements[layout.itemAt(i).widget()] = type(layout.itemAt(i).widget()).__name__

        return uiElements

    def clearFields(self, allFields:bool, showWarning:bool):
        if showWarning:
            if self.contWindow.exec() == 0: return

        with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json')) as file:
            config = json.loads(file.read())

        # Non-itterable items
        self.window.ns_rma.clear()
        self.window.ns_rma.setEnabled(True)
        self.window.ns_customer_entry.clear()
        self.window.ns_customer_entry.setEnabled(True)
        self.window.ns_so.setText("SO")
        self.window.ns_so.setEnabled(True)
        self.window.jira_ticket_entry.setText("CST-")
        self.window.jira_ticket_entry.setEnabled(True)
        self.window.svcComments.clear()
        self.window.svcComments.setEnabled(True)
        self.window.tech.setText(config["APP_PREF"]["app_tech"])
        self.window.tech.setEnabled(True)
        self.window.ths_module_fw.setText("15")
        self.window.ths_module_fw.setEnabled(True)

        self.updateDate()

        # If we are clearing ALL fields (reset to default), we need to reset every view in the tab widget (each tab)
        if allFields:
            # for the range of tabs
            # get the tab name and its children in the view
            # if the type/class of the child is in (combobox, checkbox, linedit, plainTextedit) then we need to clear it out
            # if the child needs a default value, we can check its objectName against a dict and set the corresponding value
            pass

    def setupDataValidators(self):
        try:
            # For each field that has a validator, set it here and return


            return 0
        except Exception as e:
            return e

    def checkIsValidInput(self, children):
        for child in children:
            if type(child).__name__ != 'QLineEdit': continue # Skip this itteration
            if not child.hasAcceptableInputs(): return 1 # If bad input, return err
        return 0 # Otherwise, done and continue with code




#############
# Main Loop #
#############

# Application can not be called as a deamon or child of another application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if platform.system() == "Windows": app.setStyle("Fusion")

    #Load UI(s)
    ui = mainUI(app)
    pop = startPopUp()

    # Show in order the UI windows
    pop.showpop()
    ui.showUI()
    app.exec()
