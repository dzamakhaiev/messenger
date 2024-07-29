from os import path
from os import chdir
from coverage import Coverage

cov_obj = Coverage(data_file=path.abspath(r'../.coverage'),
                   config_file=path.abspath(r'../.coveragerc'))
chdir('..')

cov_obj.start()
cov_obj.stop()
cov_obj.report()
cov_obj.xml_report()
