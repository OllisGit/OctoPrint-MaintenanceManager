# coding=utf-8
from __future__ import absolute_import
import datetime

# result is a string: "15.11.2020 20:21"
def formatDateTime(dateTimeValue):
	result = ""
	if (dateTimeValue != None):
		if (type(dateTimeValue) is datetime.datetime):
			result = dateTimeValue.strftime('%d.%m.%Y %H:%M')
		elif (type(dateTimeValue) is datetime.date):
			result = dateTimeValue.strftime('%d.%m.%Y')
		else:
			print("error formating type '"+str(type(dateTimeValue))+"' with value '"+str(dateTimeValue)+"'")
	return result


# see https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days/4048773
# 10d12h23m2s
def secondsToText(secs):
	result = ""
	days = int(secs // 86400)
	hours = int((secs - days * 86400) // 3600)
	minutes = int((secs - days * 86400 - hours * 3600) // 60)
	seconds = int(secs - days * 86400 - hours * 3600 - minutes * 60)

	if (days > 0):
		result = "{}d".format(days) + "{}h".format(hours) + "{}m".format(minutes) + "{}s".format(seconds)
	elif (hours > 0):
		result = "{}h".format(hours) + "{}m".format(minutes) + "{}s".format(seconds)
	elif (minutes > 0):
		result = "{}m".format(minutes) + "{}s".format(seconds)
	elif (seconds >= 0):
		result = "{}s".format(seconds)

    # result = ("{}d".format(days) if days else "") + \
    #          ("{}h".format(hours) if hours else "") + \
    #          ("{}m".format(minutes) if not days and minutes else "") + \
    #          ("{}s".format(seconds) if not days and not hours and seconds else "0s")
	return result# 10d12h23m2s

# mm, cm, m,  km,
def mmToText(mm):
	# result = ""
	kilo = int(mm // 1000000)
	meter  = int((mm - kilo * 1000000) // 1000)
	centi = int((mm - kilo * 1000000 - meter * 1000) // 10)
	mm = int(mm - kilo * 1000000 - meter * 1000 - centi * 10)

	if (kilo > 0):
		result = "{}k".format(kilo) + " {}m".format(meter) + " {}cm".format(centi) + " {}mm".format(mm)
	elif (meter > 0):
		result = "{}m".format(meter) + " {}cm".format(centi) + " {}mm".format(mm)
	elif (centi > 0):
		result = "{}cm".format(centi) + " {}mm".format(mm)
	elif (mm >= 0):
		result = "{}mm".format(mm)

    # result = ("{}d".format(days) if days else "") + \
    #          ("{}h".format(hours) if hours else "") + \
    #          ("{}m".format(minutes) if not days and minutes else "") + \
    #          ("{}s".format(seconds) if not days and not hours and seconds else "0s")
	return result

mm = 1111111
print(mmToText(mm))
