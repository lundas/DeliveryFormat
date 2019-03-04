#! /usr/bin/env/ python
import sys
import logging
from src import EkosSelenium
from src import renamefile
from src import datareformat
from src import sendemail
from datetime import date

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create file handler
fh = logging.FileHandler('DeliveryFormat/deliveryformat.log') # PATH to file on local machine
fh.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Add formatter to fh
fh.setFormatter(formatter)
# Add fh to logger
logger.addHandler(fh)

# Initialize classes
ekos = EkosSelenium.EkosSelenium()
rename = renamefile.RenameFile()
reformat = datareformat.DataReformat()
email = sendemail.SendEmail()

# Define variables
# Ekos
eUsername = 'EKOS USERNAME'
ePassword = 'EKOS PASSWORD'
PATH = '/PATH/TO/FILES/'	# PATH on local machine
sf = 'Delivery Hours - SF'
sac = 'Delivery Hours - Sac'
eb = 'Delivery Hours - East Bay'
sb = 'Delivery Hours - South Bay'
nb = 'Delivery Hours - North Bay'
today = date.today()
dotw = date.weekday(today)	# Day of the Week for tomorrow - today in UTC
# Send email
message = 'Here are the delivery hours for tomorrow\'s deliveries. Errors listed below:\n\n'
subject = 'Delivery Hours %s' % str(today.replace(day=today.day))
emailTo = ['LIST OF EMAILS']
emailFrom = 'EMAIL USERNAME'
password = 'EMAIL PASSWORD'

# Determines which reports to download based on dotw. If no delivery day appends message
# and sends email without attachments
try:
	if dotw == 1:	# Tuesday
		report1 = sb
		report2 = eb
	elif dotw == 2:	# Wednesday
		report1 = sf
		report2 = sac
	elif dotw == 3:	# Thursday
		report1 = eb
		report2 = nb
	elif dotw == 4:	# Friday
		report1 = sb
		report2 = sf
	else:
		sys.exit()

	ekos.login(eUsername, ePassword)

	# download and rename first report
	r1Time = ekos.download_report(report1)
	rename.rename_file(report1+'.csv', PATH)

	# download and rename second report
	r2Time = ekos.download_report(report2)
	rename.rename_file(report2+'.csv', PATH)

	ekos.quit()

	# reformat data and collect errors
	errors = reformat.data_reformat(PATH, report1+'.csv')
	errors += reformat.data_reformat(PATH, report2+'.csv')
	# join errors into string and append to message
	errors = '\n'.join(errors)
	message += errors
	fileToSend = [PATH+report1+'.csv', PATH+report2+'.csv']

	# Send email
	email.send_email(message, subject, emailTo, emailFrom, password, fileToSend)

except SystemExit:
	logger.exception('Program was exited due to no deliveries tomorrow')
	message = 'Tomorrow is not a delivery day. No files attached'
	email.send_email(message, subject, emailTo, emailFrom, password)
except:
	ekos.quit()


