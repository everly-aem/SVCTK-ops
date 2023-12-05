# This Python file uses the following encoding: utf-8

# Title: FTS Service Toolkit Main File
# Author: Everly Larche - Integrations Specalist
# Rev: 0.0.4
# Date: 2023-12-05

# This souce is not designed to be read by the end user
# This source uses open-source libraies and is not permitted to be dist. to anyone outside AEM

################################
# Imports and required Modules #
################################
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
    _loggerFormat = '[%(name)s] -- [%(levelname)s] -- [CodeLine:%(lineno)d] -- [%(asctime)s] --> %(message)s'

    #
    # BEGIN SETUP #
    def __init__(self, loggerName:str)->None:
        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(logging.INFO)

        # Directory for logs files to be placed into
        if not os.path.exists(os.path.join('_log')): os.mkdir(os.path.join('_log'))

        # Create Handlers
        cHandle = logging.StreamHandler()
        fHandle = logging.FileHandler(os.path.join('_log', 'FTS Toolkit Log.txt'), 'w')

        cHandle.setLevel(logging.INFO)
        fHandle.setLevel(logging.INFO)

        # Set the formatting
        cHandle.setFormatter(logging.Formatter(self._loggerFormat))
        fHandle.setFormatter(logging.Formatter(self._loggerFormat))

        # Add the handlers to the logger
        self.logger.addHandler(cHandle)
        self.logger.addHandler(fHandle)

        self.logger.info('Logger Created, begin logging.')

        #
        # END SETUP #

################

class startPopUp():
    # Running this as own class to ensure it happens before the main window is loaded and shown
    def __init__(self):
        self.popUp = uic.loadUi(os.path.join('_internal', 'startWarning.ui'))

    def showpop(self):
        # Executing the popup holds control until the window is closed
        self.popUp.exec()

################

class mainUI():
    #
    # Classwide variables/values
    commitData = []
    _absDIR = os.getcwd()

    #
    # BEGIN SETUP #
    def __init__(self, appREF:QtWidgets.QApplication, mainUILogger:logging.Logger)->None:
        '''
        Main setup function for the class mainUI.
        '''
        self.logger = mainUILogger

        try:
            self.logger.info('Loading configuration file.')
            with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json')) as file:
                config = json.loads(file.read())
        except Exception as e:
            self.exceptionHandler(e)
            return None

        #
        # Grab all UI elements that may be needed during startup
        self.logger.info('Setting up UI elements')

        try:
            self.window = uic.loadUi(os.path.join('_internal', 'mainwindow.ui'))
            self.loadSNWindow = uic.loadUi(os.path.join('_internal', 'loadSNWindow.ui'))
            self.loadSettingsWindow = uic.loadUi(os.path.join('_internal', 'settings.ui'))
            self.commitQueueWindow = uic.loadUi(os.path.join('_internal', 'commitQueue.ui'))
            self.contWindow = uic.loadUi(os.path.join('_internal', 'continue.ui'))
            self.taskCompleteWindow = uic.loadUi(os.path.join('_internal', 'doneTask.ui'))
            self.searchResults = uic.loadUi(os.path.join('_internal', 'searchResults.ui'))
            self.about = uic.loadUi(os.path.join(self._absDIR, '_internal', 'about.ui'))
            self.error = uic.loadUi(os.path.join(self._absDIR, '_internal', 'taskError.ui'))
            self.dms = uic.loadUi(os.path.join(self._absDIR, '_internal', 'DMS.ui'))
        except Exception as e:
            self.exceptionHandler(e)
            return None

        #
        # Establish button connectors
        self.logger.info('Creating relationships between buttons and functions')

        try:
            self.window.commitTHS.clicked.connect(lambda: self.addToQueue())
            self.window.PushtoDB.clicked.connect(lambda: self.pushToDB())
            self.commitQueueWindow.remove_from_queue.clicked.connect(lambda: self.removeFromQueue(self.commitQueueWindow.list_commit.currentRow()))
            self.loadSNWindow.buttonBox.accepted.connect(lambda: self.searchForEntry(self.loadSNWindow.sn.text()))
            self.searchResults.buttonBox.accepted.connect(lambda: self.loadEntry(self.searchResults.search_list.currentRow()))
            self.searchResults.generate_report.clicked.connect(lambda: self.generatePDFreport(self.searchResults.search_list.currentRow()))
            self.loadSettingsWindow.save_settings.clicked.connect(lambda: self.loadSettings(True))
            self.window.clear_all_fields.clicked.connect(lambda: self.clearFields(True, True))
        except Exception as e:
            self.exceptionHandler(e)
            return None

        #
        #Establish toolbar connectors
        self.logger.info('Creating toolbar connectors')

        try:
            self.window.actionSettings.triggered.connect(lambda: self.loadSettings(False))
            self.window.actionLoad_SN.triggered.connect(lambda: self.loadSNWindow.exec())
            self.window.actionCommit_Queue.triggered.connect(lambda: self.showFromToolbar(signal=2))
            self.window.actionClear_Fields.triggered.connect(lambda: self.clearFields(True, True))
            self.window.actionAbout.triggered.connect(lambda: self.loadAbout())
            self.window.actionLinks_to_DMS.triggered.connect(lambda: self.dms.exec())
        except Exception as e:
            self.exceptionHandler(e)
            return None

        #
        # Other UI Set-up
        self.logger.info('Working on other UI elements')

        try:
            self.updateDate()
            self.window.date_of_entry.setText(self.todaysDate+" (Current)")
            # Used for referencing the application object in setting os cursor
            self.app = appREF
            self.window.tech.setText(config["APP_PREF"]["app_tech"])
            self.window.tabWidget.setCurrentIndex(config["APP_PREF"]["app_start_tab"])
        except Exception as e:
            self.exceptionHandler(e)
            return None

        #
        # Setup data validators
        # Non-itterable first
        self.logger.info('Setting non-itterable UI input data validators')

        try:
            self.window.ns_rma.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('RMA\-[0-9][0-9][0-9][0-9]')))
            self.window.ns_customer_entry.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[0-9][0-9][0-9][0-9][0-9][0-9]')))
            self.window.ns_so.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('SO[0-9][0-9][0-9][0-9][0-9]')))
            self.window.jira_ticket_entry.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('CST\-[0-9][0-9][0-9][0-9]')))
        except Exception as e:
            self.exceptionHandler(e)
            return None

        # Loop over each tab and set the item validators per tab
        try:
            for i in range(self.window.tabWidget.count()):
                self.logger.info(f'Setting input data validators for tabWidget index{i}')
                serialValidator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[0-9][0-9][0-9][0-9][0-9][0-9]'))
                ths3FWValidator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[0-9][0-9]'))

                match i:
                    case 1:
                        self.window.FS_SN.setValidator(serialValidator)
                        self.window.fs_module_sn.setValidator(serialValidator)
                        self.window.fs_module_fw.setValidator(ths3FWValidator)
                    case 2:
                        self.window.ths_sn.setValidator(serialValidator)
                        self.window.ths_module_sn.setValidator(serialValidator)
                        self.window.ths_module_fw.setValidator(ths3FWValidator)
        except Exception as e:
            self.exceptionHandler(e)
            return None


        self.logger.info('Setup complete!')
        return None
        #
        # END SETUP #



    ################

    # Class Functions
    def loadAbout(self)->None:
        '''
        Loads build info to the About UI when opened.
        '''
        try:
            with open(os.path.join('_internal', 'FTSTK_config.json')) as jsonFile:
                config = json.loads(jsonFile.read())
            config = config['Build']
        except Exception as e:
            self.exceptionHandler(e)

        try:
            self.about.application_ver.setText(config['Version'])
            self.about.build.setText(config['Build'])
            self.about.debug_active.setText(str(config['Debug']))
            if not config['FullRelease']:
                self.about.build_mode.setText('Work-in-progress Copy')
            else:
                self.about.build_mode.setText('Full Release')
        except Exception as e:
            self.exceptionHandler(e)
            return None

        self.about.exec()
        return None

    def updateDate(self)->None:
        '''
        Updates the date when it should be refreshed.
        Need to add the ability to get the date from a loaded entry.
        '''
        self.logger.info('Updating the date')
        self.todaysDate:str = datetime.datetime.today().strftime("%Y-%m-%d")
        self.window.date_of_entry.setText(self.todaysDate+" (Current)")
        self.logger.info(f'Update the date to: {self.todaysDate}')
        return None

    def showUI(self)->None:
        '''
        Used to display the main Window.
        '''
        self.window.show()

    # to show ui/windows based on button press mapped to case#
    def showFromToolbar(self, signal)->None:
        '''
        Basic match case for toolbar functions. May be deprecated in later version.
        '''
        self.logger.info('Showing from toolbar')
        match signal:
            case 0:
                self.loadSettingsWindow.exec() #exec function are BLOCKING
            case 1:
                self.loadSNWindow.exec()
            case 2:
                try:
                    # Create list used to hold the information to show on UI window
                    displaySN = []
                    for items in self.commitData:
                        displaySN.append(items["destCollection"] + " --> SN:" + items["Serial_Number"])

                    self.logger.info(f'Serial numbers found to display:\n{displaySN}')
                    self.commitQueueWindow.list_commit.addItems(displaySN)
                    self.commitQueueWindow.exec()
                    self.commitQueueWindow.list_commit.clear() # Must clear UI list after each use, otherwise all calls will append
                except Exception as e:
                    self.exceptionHandler(e)
                    return None
        return None

    # Det. what to commit depending on tab widget index as case statement
    def addToQueue(self)->None:
        '''
        Depending on the currently selected sensor tab, grab all applicable data needed to enter an entry into the queue.
        Then add the data into the queue for submission.
        '''
        self.logger.info('Adding item to the queue')
        # Use the index of the current tab to determine what sensor type is being added to the queue
        signal:int = self.window.tabWidget.currentIndex()

        # Check if the user is sure, if not, end function do not grab data
        self.contWindow.title.setText('Add to queue?')
        if self.contWindow.exec() == 0:
            self.logger.info('Add to queue aborted!')
            return None

        # Matching the index of the tabWidget to det. what sensor is being used
        # Try to open the files needed and grab data programtically
        try:
            self.logger.info(f'Looking for index:{signal}')
            match signal:
                case 0:
                    with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'fs_template.json'), 'r') as jsonFile:
                                template = json.loads(jsonFile.read())
                    with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'fs_translation.json'), 'r') as jsonFile:
                                translation = json.loads(jsonFile.read())
                    childrenToItterate = self.window.THS_scroll_area_contents.children()

                case 1:
                    with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'ths_template.json'), 'r') as jsonFile:
                                template = json.loads(jsonFile.read())
                    with open(os.path.join(self._absDIR, '_internal', '__templateStructs', 'ths_translation.json'), 'r') as jsonFile:
                                translation = json.loads(jsonFile.read())

                    childrenToItterate = self.window.FS_scroll_area_contents.children()

                case _:
                    raise Exception('Unable to match the case!')

            try:
                self.logger.info('Checking for valid inputs before adding to the queue...')
                isValid = self.checkIsValidInput('', self.window.is_for_swapPool.isChecked()) # Get children outside of match case
            except Exception as e:
                self.exceptionHandler(e)
                return None

            if not isValid:
                self.logger.warning('Inputs are NOT VALID! Aborting add to queue')
                self.error.title.setText('Invalid Inputs!')
                self.error.message.setText('Please verify all inputs are entered correctly before continuing!')
                self.error.exec()
                return None

            self.logger.info('Inputs valid, moving on to adding information into the queue')
            self.logger.info('Attempting to load templateStructs')

            self.getNonItterable(template)
            self.childrenData(children=childrenToItterate, template=template, translation=translation, get=True, set=False)

        except Exception as e:
            self.exceptionHandler(e)
            return None

        # Clear the fields that have been read by the ths_template
        self.clearFields(True, False)

        # Preform other tasks when adding to the queue
        self.logger.info('PushtoDB button enabled.')
        self.window.PushtoDB.setEnabled(True)
        self.taskCompleteWindow.exec()
        return None

    def getNonItterable(self, template)->dict:
        '''
        Used to get data from the common elements on the UI.
        '''
        try:
            self.logger.info('Running getNonItterable()')

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
        except Exception as e:
            self.exceptionHandler(e)
            return None # Will throw another error, to be handled, user will be notified

    def childrenData(self, children, template, translation, get:bool, set:bool)->None:
        '''
        Works on getting or setting data to/from children in a spesified list of child widgets.
        '''
        self.logger.info('Getting child data from UI layouts')

        if get: entry:dict = template

        try:
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
        except Exception as e:
            self.exceptionHandler(e)
            return None

        try:
            if get: self.commitData.append(entry)
        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def nestedData(self, target, targetKey, value, get:bool, set:bool)->any:
        '''
        Uses recursion to find a key:value pair in a nested dictionary.
        Works bi-directional for get/set, returns any value found for the key.
        '''
        self.logger.info('Getting nested data...')

        try:
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

        except Exception as e:
            self.exceptionHandler(e)
            return

    def pushToDB(self)->None:
        '''
        Push the queued data to the DB with the correct collections.
        '''
        self.logger.info('Starting push to DB...')

        # Check if the user is sure, if not, end function do not grab data
        self.contWindow.title.setText('Push to DB?')
        if self.contWindow.exec() == 0:
            self.logger.warning('User aborted push!')
            return

        db = mongoHandler()
        if db.pushCollection(self.commitData) != 0:
            self.logger.warning('Issue with pushing data to the DB!')
            self.error.title.setText('Issue with pushing to the DB!')
            self.error.message.setText('')
            self.error.exec()

        # Need to clear queue after commit and disable push to db button
        try:
            self.logger.info('Resetting for another entry to be made...')
            self.commitData = []
            self.window.PushtoDB.setEnabled(False)
            self.commitQueueWindow.list_commit.clear()
            self.taskCompleteWindow.exec()

        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def removeFromQueue(self, index:int)->None:
        '''
        Removes an item from the queue, if empty disable the push to DB function.
        '''
        self.logger.info(f'Removing index:{index} from the queue!')

        try:
            self.commitQueueWindow.list_commit.takeItem(index)
            if len(self.commitData) > 0: self.commitData.pop(index)
            self.logger.info(f'Data remaining in queue: {self.commitData}')
            if len(self.commitData) <= 0: self.window.PushtoDB.setEnabled(False)

        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def searchForEntry(self, serialNumber:str)->None:
        '''
        Searches all DB collections for the spesified serach term/field.
        Lists all found items in the UI directly.
        '''
        self.logger.info(f'Looking for {serialNumber}')
        db = mongoHandler()
        self.dbData = []

        try:
            self.logger.info('Getting from DB collection')
            self.dbData = db.getCollection(serialNumber)
        except Exception as e:
            self.exceptionHandler(e)
            return None

        self.logger.info('Data found! Listing in UI...')
        displaySN = []
        for entry in self.dbData:
            displaySN.append(entry["destCollection"] + " --> SN:" + entry["Serial_Number"] + f"  [{entry['Date_of_Entry']}]")
        try:
            self.searchResults.label.setText(f"{len(displaySN)} Results Found:")
            self.searchResults.search_list.addItems(displaySN)
            self.searchResults.exec()
            self.searchResults.search_list.clear()
        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def loadEntry(self, index:int)->None:
        '''
        Takes an index:int to isolate data in the retrived list of dicts retrived from the DB
        '''
        self.logger.info('Starting to load entry into UI for observation...')

        # Check if the user is sure, if not, end function do not grab data
        self.contWindow.title.setText('Load Data into UI?')
        if self.contWindow.exec() == 0:
            self.logger.warning('User aborted loading data into UI!')
            return

        # Clear out all other entries from mem. apart from the one we want to load
        self.dbData = self.dbData[index]
        type:str = self.dbData["destCollection"]
        self.logger.info(f'Loading data for type:{type}')
        try:
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

            self.window.date_of_entry.setText(self.dbData["Date_of_Entry"]+" (Date of Entered)")

        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def generatePDFreport(self, index:int)->None:
        '''
        Attempts to use WKHTMLTOPDF to generate a report from the loaded data in the DB.
        '''
        self.logger.info('Generating PDF file...')
        self.showBusy(True)
        data = self.dbData[index]
        generator = MakePDF()
        rc = generator.render(data["destCollection"], data, self.todaysDate)
        self.showBusy(False)
        if rc == 0:
            self.showCompleteWindow("Generate PDF Complete!", "Genderated PDF file was created and saved to your output foler.")
        else:
            self.logger.warning(f'Expected RC of 0, got:{rc}')
            self.logger.error('PDF Generation failed.')
            self.error.title.setText('PDF Failed!')
            self.error.message.setText(f'Failed to generate PDF... Expected RC of 0, got {rc}')
            self.error.exec()
        return None

    def showCompleteWindow(self, task:str, message:str)->None:
        '''
        Displays the task completed window with the spesified message and title.
        '''
        self.logger.info('A task completed, showing complete window')
        try:
            self.taskCompleteWindow.title.setText(task)
            self.taskCompleteWindow.message.setText(message)
            self.taskCompleteWindow.exec()
        except Exception as e:
            self.exceptionHandler(e)
            return None
        return None

    def showBusy(self, TF:bool)->None:
        '''
        Overrides the main cursor of the machine to display a background function in progress.
        '''
        try:
            if TF: app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
            else: app.restoreOverrideCursor()
        except Exception as e:
            self.exceptionHandler(e)
            return

    def loadSettings(self, set:bool)->None:
        '''
        Either loads settings to be displayed un UI or
        takes settings entered into the UI and saves them in the applications configuration file.
        '''
        self.logger.info('Loading settings...')
        try:
            with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json'), 'r') as configFile:
                config = json.loads(configFile.read())
        except Exception as e:
            self.exceptionHandler(e)
            return

        # Unpact only the required items from the configuration file as smaller dicts
        self.logger.info('Unpacking settings...')
        SETTING:dict = {**config["DB"], **config["APP_PREF"], **config["PDF_PREF"]}

        # Set up whats needed in the UI based on the settings avaliable (ex. the collections being used)
        try:
            if not set:
                widgets = self.layoutWidgets(self.loadSettingsWindow.settingsLayout)
                for widget in widgets.keys():
                    self.logger.info(f'Loading widget:{widget.objectName()}')
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

                self.loadSettingsWindow.exec()
        except Exception as e:
            self.exceptionHandler(e)
            return None

        if set:
            try:
                for key in SETTING.keys():
                    self.nestedData(config, key, SETTING[key], False, True)
                self.logger.info(f'New config to be saved as JSON: {config}')
                jsonString = json.dumps(config, indent=6)
                self.logger.info(f'JSON String to be saved: {jsonString}')
                with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json'), 'w') as configFile:
                    configFile.write(jsonString)

                self.showCompleteWindow("Settings Saved!", "Some settings may not apply until the application is restarted.")
            except Exception as e:
                self.exceptionHandler(e)
                return None
        return None

    def layoutWidgets(self, layout)->dict:
        '''
        Searches over a spesified layout for all child elements that match the criteria of being a widget.
        Discard all others.
        '''
        self.logger.info('Searching for widgets inside a layout...')

        # Empty dict to store all the elements in
        uiElements = {}

        # For each item in the layout (up to the max in the layout), get the name of the widget and its type(class), append it to the dict and return
        try:
            for i in range(layout.count()):
                if type(layout.itemAt(i)).__name__ == 'QWidgetItem':
                    uiElements[layout.itemAt(i).widget()] = type(layout.itemAt(i).widget()).__name__

            return uiElements
        except Exception as e:
            self.exceptionHandler(e)
            return None # Show throw error and will be handled later, will show another err to the user

    def clearFields(self, allFields:bool, showWarning:bool)->None:
        '''
        Clears either all input fields to their default or only common fields.
        '''
        self.logger.info('Clearing all input fields...')

        if showWarning:
            self.contWindow.title.setText('Clear all fields?')
            if self.contWindow.exec() == 0:
                self.logger.warning('User aborted the action!')
                return None

        try:
            # Getting the config to load the tech default name
            with open(os.path.join(self._absDIR, '_internal', 'FTSTK_config.json')) as file:
                config = json.loads(file.read())
        except Exception as e:
            self.exceptionHandler(e)
            return None

        # Non-itterable items/common elements
        try:
            self.window.ns_rma.clear()
            self.window.ns_rma.setEnabled(True)
            self.window.ns_customer_entry.clear()
            self.window.ns_customer_entry.setEnabled(True)
            self.window.ns_so.clear()
            self.window.ns_so.setEnabled(True)
            self.window.jira_ticket_entry.clear()
            self.window.jira_ticket_entry.setEnabled(True)
            self.window.svcComments.clear()
            self.window.svcComments.setEnabled(True)
            self.window.tech.setText(config["APP_PREF"]["app_tech"])
            self.window.tech.setEnabled(True)

            # This needs to be in the child section
            self.window.ths_module_fw.setText("15")
            self.window.ths_module_fw.setEnabled(True)

            self.updateDate()

        except Exception as e:
            self.exceptionHandler(e)
            return None

        # If we are clearing ALL fields (reset to default), we need to reset every view in the tab widget (each tab)
        if allFields:
            # for the range of tabs
            # get the tab name and its children in the view
            # if the type/class of the child is in (combobox, checkbox, linedit, plainTextedit) then we need to clear it out
            # if the child needs a default value, we can check its objectName against a dict and set the corresponding value
            pass
        return None

    def checkIsValidInput(self, children, isSP:bool)->bool:
        '''
        Over all applicable fields, check inputs match the validators.
        Return T/F.
        '''
        self.logger.info('Checking for valid inputs on selected children...')
        # Check inputs that are used across all tabs, all must be true otherwise return 1
        if not (
            self.window.ns_rma.hasAcceptableInput() and
            (self.window.ns_customer_entry.hasAcceptableInput() or isSP) and # either or, if SP then will still be true, but will fail if not SP and invalid
            self.window.ns_so.hasAcceptableInput() and
            self.window.jira_ticket_entry.hasAcceptableInput()
        ):
            self.logger.warning('Exit checkIsValid, found something invalid!')
            return False

        # Checking itterable child elements of tab
        try:
            for child in children:
                if type(child).__name__ != 'QLineEdit': continue # Skip this itteration
                if not child.hasAcceptableInputs(): return False # If bad input, return err

            return True # Otherwise, done and continue with code
        except Exception as e:
            self.exceptionHandler(e)
            return False

    def exceptionHandler(self, e)->None:
        '''
        Function for handling when an exception is made.
        Places messages in both: logger & Error UI.
        '''
        title:str = str(type(e).__name__)
        message:str = str(e)

        self.logger.error(title)
        self.logger.exception(message)
        self.error.title.setText(title)
        self.error.message.setText(message)
        self.error.exec()
        return None


#############
# Main Loop #
#############

# Application can not be called as a deamon or child of another application
if __name__ == "__main__":
    uiLogger = myLogger('uiLogger')
    uiLogger = uiLogger.logger

    app = QtWidgets.QApplication(sys.argv)
    if platform.system() == "Windows": app.setStyle("Fusion") # Allows for system theme application in WindowsOS

    #Load UI(s)
    ui = mainUI(app, uiLogger)
    pop = startPopUp()

    # Show in order the UI windows
    pop.showpop()
    ui.showUI()
    app.exec()
