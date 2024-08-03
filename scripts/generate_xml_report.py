from os import path
from coverage import Coverage

current_file = path.realpath(__file__)
current_dir = path.dirname(current_file)
data_file = path.abspath(path.join(current_dir, '..', '.coverage'))
out_file = path.abspath(path.join(current_dir, '..', 'coverage.xml'))


cov_obj = Coverage(data_file=data_file)
if path.isfile(data_file):
    cov_obj.load()
    cov_obj.xml_report(outfile=out_file, skip_empty=True)
