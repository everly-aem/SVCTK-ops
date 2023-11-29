import pdfkit, os
from jinja2 import Environment, FileSystemLoader
from io import StringIO

class MakePDF:
    data = {
        "_id": {
            "$oid": "65661f57e5967659a12d304a"
        },
        "destCollection": "FS",
        "Serial_Number": "112233",
        "Date_of_Entry": "2023-11-28",
        "SVC_Details": {
            "NS_RMA": "RMA-TESTFS",
            "NS_Customer": "FTS TESTFS",
            "NS_Parts_SO": "SO-TESTFS",
            "Jira_Ticket": "CST-TESTFS",
            "THS_Sensor_Info": {
            "00-THS-3_Serial_Number": "009988",
            "Model_Option": "FS-3-R",
            "Incoming_Status": "Other (Desc. in Comments)"
            },
            "Incoming_and_Visual": {
            "Passed_Checks": "Failed - Explain in Comments",
            "00-THS-3_FW_Ver": "15",
            "Visual_Complete": True,
            "Cleaned": True,
            "Incoming_Notes": "INCOMINGNOTES"
            },
            "Calibration_and_Servicing": {
            "Incoming_RH": "Unable to Test",
            "Incoming_Temp": "Unable to Test",
            "Required_Repairs": "Repairs Preformed",
            "RH_Calibrated": "Wafer Replaced - Recalibrated",
            "Builentins_Used": "Yes - See Comments",
            "Active_Current_Pass": True,
            "Filter_Replaced": True,
            "Desiccant_Replaced": True,
            "RH_Calibration_Pass": True,
            "Temp_Calibration_Pass": True,
            "CTM_Installed": True,
            "Dowel_Replaced": "Yes"
            },
            "Service_Comments": "The techs service comments will go here",
            "Warranty_Status": "No Warranty",
            "Tech": "Everly TESTING"
        }
    }

    def __init__(self) -> None:
        # Get pdf options from main cfg
        pass

    def insertData(self, type:int, data):
        # Depending on what sensor type, open the correct template and fill
        env = Environment(loader=FileSystemLoader(os.path.join('_internal', '__reports')))
        match type:
            case 0:
                template = env.get_template("fs_report_template.html")
                content = template.render(data=data)
                self.generateReport(content)
    
    def generateReport(self, htmlFile):
        # Using the filled html file, generate the report, placed in the correct DIR
        # and return the status
        options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'no-outline': None
        }

        pdfkit.from_string(htmlFile, output_path='testFile.pdf', options=options)