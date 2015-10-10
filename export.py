from main.models import *

import csv

# bb=["AAA", "ABC", "ARBT", "ARMG", "AWS", "BLCK", "CIV", "EEP", "ENVS", "FYS", "GMST", "HSS", "INFO", "MILS", "MUS0", "MUS1", "MUSI", "NR", "PUBP", "REL", "SIPZ", "SPE", "SPEC", "TEST", "WMST", "X", "XAST", "XECO", "XGOV", "XHIS", "XLIT", "XMAT" ]
# for b in bb:
# 	Subject(code=b).save()

def format_time(ts):
	ampm = ts[-2:]
	[hour,minute] = ts[:-2].split(":")
	hour = int(hour)
	minute = int(minute)
	if ampm == "pm": hour += 12
	if hour == 12: hour = 0
	if hour == 24: hour = 12
	return hour + minute / 60.0

f = open("courses.csv","w")
a = csv.writer(f, delimiter=",")
count = 0
bigcount = 0
for meeting in PortalMeeting.objects.all():
	count += 1
	if count == 1000:
		count = 0
		bigcount += 1
		print bigcount
	section = meeting.section
	course = section.course
	try:
		subject = course.subject
	except:
		subject = Subject(code=subject_code,name=subject_code)
		subject.save()
		print "Add",subject
	course_no = int(course.course_no[:3])
	year = course.semester[:2]
	semester = course.semester[2:]
	start = format_time(meeting.start)
	end = format_time(meeting.end)
	if end <= start: continue
	a.writerow([course.course_code,subject.name,  year, semester, subject.code, course_no, section.campus, meeting.day, start, end])

f.close()
