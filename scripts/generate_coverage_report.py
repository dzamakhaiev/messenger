from coverage import Coverage

cov_obj = Coverage(data_file=r'../.coverage', config_file=r'../.coveragerc')
cov_obj.start()
cov_obj.stop()
cov_obj.report()
cov_obj.xml_report()
