import pdfkit, os, json
from jinja2 import Environment, FileSystemLoader

class MakePDF:

    _cwd = os.getcwd()

    def __init__(self, pdfLogger) -> None:
        self.logger = pdfLogger

        self.logger.debug(f'CWD from pdfGenerator: {self._cwd}')

        # Get pdf options from main cfg
        self.logger.debug('Opening Config file')
        with open(os.path.join(self._cwd, '_internal', 'FTSTK_config.json')) as file:
            self.cfg = json.loads(file.read())

    def render(self, type:str, data:dict, date:str):
        self.logger.debug('Called render()')
        # Depending on what sensor type, open the correct template and fill
        env = Environment(loader=FileSystemLoader(os.path.join(self._cwd, '_internal', '__reports')))
        self.logger.debug(f'Loaded env: {env}')
        match type:
            case 'FS':
                template = env.get_template("fs_report_template.html")
            case 'THS':
                template = env.get_template("ths_report_template.html")
            case _:
                self.logger.warning('UNABLE TO MATCH CASE')
        content = template.render(data=data)

        # Using the filled html file, generate the report, placed in the correct DIR
        # and return the status
        options = {
                'page-size': 'A4',
                'margin-top': '0in',
                'margin-right': '0.25in',
                'margin-bottom': '0.35in',
                'margin-left': '0.25in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'no-outline': None,
                'footer-center': '[page] of [topage]',
                'footer-left':'ISO-SV-F-XXXX\nRev: 0',
                'footer-right':f'Report Generated on: {date}',
                'footer-font-size': 10
        }
        enginePath = os.path.join(self._cwd, '_internal', 'wkhtmltox', 'bin', 'wkhtmltopdf.exe')
        self.logger.debug(f'Path to engine used: {enginePath}')
        config = pdfkit.configuration(wkhtmltopdf=enginePath)
        self.logger.debug(f'Loaded config with path: {enginePath}')
        try:
            self.logger.debug('Generating PDF...')
            outPath = os.path.join(os.path.normpath(self.cfg["PDF_PREF"]["pdf_output"]),data["Serial_Number"]+type+date+'.pdf')
            self.logger.debug(f'PDF output path is: {outPath}')
            pdfkit.from_string(content, output_path=outPath, options=options, configuration=config)
        except Exception as e:
            self.logger.error('Exception occured when calling pdfkit.from_string()!')
            self.logger.exception(e)
            return e

        self.logger.info('pdfGenerator.py complete!')
        return 0
