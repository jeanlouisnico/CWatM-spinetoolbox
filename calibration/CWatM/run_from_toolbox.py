import sys

from cwatm import __author__, __version__, __date__, __copyright__, __maintainer__, __status__
from cwatm.run_cwatm import main, mainwarm, parse_args, usage, GNU


settings = 'settings_CWatM_template_30min.ini'
args = ['-l']
main(settings, args)