import csv

from main.models import Dorm, DormRoom, Student, Roster


departments = {}
f = open("main/prepare/roster.csv","rU")
for row in csv.reader(f):
	row = map(lambda x:x.strip(),row)
	# Fullname, Nickname, Class, Dorm, Room, Phone(Rm Cell),Email
	s = Student(email=row[6],full_name=row[0],nickname=row[1])
	print s.full_name
	names = row[0].split(",")
	if (len(names) == 2):
		s.last_name,s.first_name = names
	else:
		assert(len(names) == 3)
		s.last_name = names[0]
		s.first_name = names[1]
	s.save()
	r = Roster(student=s,semester="SP14",class_code=row[2])
	if row[3] not in ["Abroad","Off","Scripps","Pomona"]:
		# Get the dorm object
		try:
			dorm = Dorm.objects.get(name=row[3])
		except:
			dorm = Dorm(name=row[3])
			dorm.save()
		# Get the room object
		try:
			room = DormRoom.objects.get(building=dorm,room_no=row[4])
		except:
			room = DormRoom(building=dorm,room_no=row[4])
			room.save()
		r.room = room
	if row[5]: # phone
		phones = row[5].split(",")
		if len(phones) == 1:
			r.cell_phone = row[5]
		else:
			r.room_phone = phones[0]
			r.cell_phone = phones[1]
	r.save()
f.close()
