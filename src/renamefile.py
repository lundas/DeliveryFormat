from datetime import datetime, date
from pytz import timezone
import os
import re
import sys
import logging

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

class RenameFile:
	'''Class for renaming files downloaded from Ekos in preperation for
	reformatting data using pandas and then importing data into Google
	Sheets'''

	def dtround(self, datetime):
		'''Rounds seconds of datetime object up if microseconds > 500000
		else returns datetime object'''
		logger.info("Rounding %s" % str(datetime))
		if datetime.microsecond > 500000 and datetime.second == 59:
			datetime = datetime.replace(minute = datetime.minute + 1, 
				second = 0)
		elif datetime.microsecond > 500000:
			datetime = datetime.replace(second = datetime.second + 1)
		return datetime

	def tzconv(self, datetime):
		'''Takes datetime object, sets timezone as Pacific Time
		and the convents timezone to Eastern Time. Necessary because
		Ekos export names incorporate time of download in Eastern Time.
		DST = Daylight Savings Time'''
		logger.info("Adjusting Timezones")
		datetime = timezone('UTC').localize(datetime)
		datetime = datetime.astimezone(timezone('US/Eastern'))
		logger.debug('Adjusted Timezone is %s' % str(datetime))
		return datetime

	def rename_file(self, datetime, new_filename, PATH):
		'''takes given datetime and uses it to create a string that
		matches the filename of recently downloaded ekos export. Then
		searches PATH directory for the desired file and renames file
		to new filename provided by user '''
		filename = 'Export_%s_.csv' % datetime.strftime("%m%d%Y%I%M%S")
		count = 0
		exit = False
		try:
			while os.path.isfile(PATH + filename) is False and exit is False:
				try:
					datetime = datetime.replace(second = datetime.second + 1)
					count = count + 1
					logger.debug(datetime)
					filename = 'Export_%s_.csv' % datetime.strftime("%m%d%Y%I%M%S")
					logger.debug(filename)
					if count == 59:
						exit = True
				except ValueError:
					logger.warning('ValueError: resetting seconds to 0. count = %d' % count)
					datetime = datetime.replace(second = 0)
					count = 0
			if exit == True:
				sys.exit()	#  Acts as failsafe against infinite loop
		except SystemExit:
			logger.exception('Exiting program due to infinite loop')

		os.rename(PATH + filename, PATH + new_filename)
		return


	
