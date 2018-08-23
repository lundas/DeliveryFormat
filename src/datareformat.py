import csv
import logging
from datetime import date, datetime

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


class DataReformat:
	# Class for reformatting Delivery Hour Report data from Ekos

	def data_reformat(self, PATH, filename):
		# Reformats data from Delivery Hour reports from Ekos
		
		logger.info('Reformatting %s data' % filename)

		# Import and read csv file located in PATH
		targetFile = PATH + filename
		deliveryFile = open(targetFile)
		deliveryReader = csv.reader(deliveryFile)
		deliveryData = list(deliveryReader)

		# check deliveryData for blank rows - avoid index errors
		index = 0
		for row in deliveryData:
			if len(row) == 0:
				deliveryData.pop(index)
			index = index + 1

		# collect addresses, cities, states and zips into lists
		addresses = []
		cities = []
		states = []
		zips = []
		errors = []  # Collects errors to be included in email

		for row in deliveryData[1:]:
			if row[3]==0 or \
			   row[4]==0 or \
			   row[5]==0 or \
			   row[6]==0:
				addresses.append(row[3])
				cities.append(row[4])
				states.append(row[5])
				zips.append(row[6])
				errors.append(row[2] + ' is missing an address')
			else:
				addresses.append(row[3])
				cities.append(row[4])
				states.append(row[5])
				zips.append(row[6])

		# zip and join lists to form single address column
		deliveryAddresses = zip(addresses, cities, states, zips)
		index = 0
		for row in deliveryAddresses:
			deliveryAddresses[index] = ", ".join(row)
			index = index + 1

		# get account names
		deliveryAccounts = []
		for row in deliveryData[1:]:
			deliveryAccounts.append(row[2])

		# Get delivery times based on delivery day of the week
		# 0 = Monday, 6 = Sunday
		deliveryFrom = []
		deliveryTo = []
		today = date.today()
		deliveryWeekday = date.weekday(today)
		for row in deliveryData[1:]:
			if deliveryWeekday == 1:
				if len(row[7]) > 0 and len(row[8]) > 0:
					deliveryFrom.append(datetime.strptime(row[7],"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime(row[8],"%m/%d/%Y %I:%M %p").time())
				else:
					deliveryFrom.append(datetime.strptime('03/13/1990 9:00 AM',"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime('03/13/1990 5:00 PM',"%m/%d/%Y %I:%M %p").time())
					errors.append(row[2] + ' is missing a delivery time')
			if deliveryWeekday == 2:
				if len(row[9]) > 0 and len(row[10]) > 0:
					deliveryFrom.append(datetime.strptime(row[9],"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime(row[10],"%m/%d/%Y %I:%M %p").time())
				else:
					deliveryFrom.append(datetime.strptime('03/13/1990 9:00 AM',"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime('03/13/1990 5:00 PM',"%m/%d/%Y %I:%M %p").time())
					errors.append(row[2] + ' is missing a delivery time')
			if deliveryWeekday == 3:
				if len(row[11]) > 0 and len(row[12]) > 0:	
					deliveryFrom.append(datetime.strptime(row[11],"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime(row[12],"%m/%d/%Y %I:%M %p").time())
				else:
					deliveryFrom.append(datetime.strptime('03/13/1990 9:00 AM',"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime('03/13/1990 5:00 PM',"%m/%d/%Y %I:%M %p").time())
					errors.append(row[2] + ' is missing a delivery time')
			if deliveryWeekday == 4:
				if len(row[13]) > 0 and len(row[14]) > 0:	
					deliveryFrom.append(datetime.strptime(row[13],"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime(row[14],"%m/%d/%Y %I:%M %p").time())
				else:
					deliveryFrom.append(datetime.strptime('03/13/1990 9:00 AM',"%m/%d/%Y %I:%M %p").time())
					deliveryTo.append(datetime.strptime('03/13/1990 5:00 PM',"%m/%d/%Y %I:%M %p").time())
					errors.append(row[2] + ' is missing a delivery time')

		# Write code that catches incorrect AM/PM Ekos entries 
		# for delivery times
		for dA,dF,dT in zip(deliveryAccounts, deliveryFrom, deliveryTo):
			if dF >= dT:
				errors.append(dA + '\'s delivery hours are entered incorrectly')

		deliveryHours = zip(deliveryAccounts, deliveryAddresses, deliveryFrom, deliveryTo)
		deliveryHours.insert(0, ('ID', 'Address', 'From', 'To')) # insert column headers

		#write info to csv file
		with open(PATH + filename, 'wb') as csvfile:
		    writer = csv.writer(csvfile, dialect = 'excel')
		    for e in deliveryHours:
		        writer.writerow(e)

		return errors


if __name__ == '__main__':
	reformat = DataReformat()

	PATH = '/PATH/TO/FILES/'
	filename = 'FILENAME'
	new_filename = 'NEW_FILENAME'

	errors = reformat.datareformat(PATH, filename, new_filename)
	print errors

