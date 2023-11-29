import pdfkit, os, json
from jinja2 import Environment, FileSystemLoader

class MakePDF:

    def __init__(self) -> None:
        # Get pdf options from main cfg
        with open(os.path.join('_internal', 'FTSTK_config.json')) as file:
            self.cfg = json.loads(file.read())

    def render(self, type:str, data, date):
        # Depending on what sensor type, open the correct template and fill
        env = Environment(loader=FileSystemLoader(os.path.join('_internal', '__reports')))
        match type:
            case 'FS':
                template = env.get_template("fs_report_template.html")
            case 'THS':
                template = env.get_template("ths_report_template.html")
        content = template.render(data=data)

        # Using the filled html file, generate the report, placed in the correct DIR
        # and return the status
        options = {
                'page-size': 'A4',
                'margin-top': '0.25in',
                'margin-right': '0.25in',
                'margin-bottom': '0.25in',
                'margin-left': '0.25in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'no-outline': None,
                'footer-center': '[page] of [topage]',
                'footer-left':'ISO-XXX-XXXX\nRev: 0',
                'footer-right':f'Report Generated on: {date}',
                'footer-font-size': 10
        }
        config = pdfkit.configuration(wkhtmltopdf=os.path.normpath(self.cfg["PDF_PREF"]["Engine_Location"]))
        try:
            pdfkit.from_string(content, output_path=self.cfg["PDF_PREF"]["Output_DIR"]+data["Serial_Number"]+type+date+'.pdf', options=options, configuration=config)
        except Exception as e:
            return e

        return 0
