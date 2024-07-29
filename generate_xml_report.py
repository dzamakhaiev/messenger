from os import path
from coverage import Coverage

data_file = path.abspath(r'.coverage')
cov_obj = Coverage(data_file=data_file)

if path.isfile(data_file):
    cov_obj.load()
    cov_obj.xml_report()
