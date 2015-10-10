from django.db import models
from datetime import datetime

##################
# Portal Section #
##################

# (R25)
class Building(models.Model):
	name = models.CharField(max_length=32, primary_key = True)
	location = models.CharField(max_length=256)

# R5
class TeachingBuilding(Building):
	full_name = models.CharField(max_length=32)

# R4
class ClassRoom(models.Model):
	building = models.ForeignKey(TeachingBuilding)
	room_no = models.CharField(max_length=32)
	class Meta:
		unique_together = ('building', 'room_no',)

# R19
class Subject(models.Model):
	code = models.CharField(max_length=8,primary_key=True)
	name = models.CharField(max_length=32)

# R1
class PortalCourse(models.Model):
	# The primary key. Example: MATH180 HM FA13
	# When subject code is less than 4 char, a space is added: MUS 171DF SC SP13
	course_code = models.CharField(max_length=32,primary_key=True)
	title = models.CharField(max_length=128)
	# The following four parse the primary key
	subject = models.ForeignKey(Subject)
	course_no = models.CharField(max_length=16)
	semester = models.CharField(max_length=16,blank=True)
	program = models.CharField(max_length=4)
	credit = models.DecimalField(max_digits=3,decimal_places=2)
	credit_adj = models.DecimalField(max_digits=3,decimal_places=2)

# update main_portalcourse set credit_adj = credit*3
# update main_portalcourse set credit_adj = credit_adj/3 where program="HM" or (program!="HM" and credit>3)

# R2
class PortalSection(models.Model):
	course = models.ForeignKey(PortalCourse)
	section = models.CharField(max_length=16,blank=True)
	campus = models.CharField(max_length=16,blank=True)
	seats_taken = models.IntegerField(blank=True,null=True)
	seats_total = models.IntegerField(blank=True,null=True)
	# Define primary key
	class Meta:
		unique_together = ('course','section')

# R3
class PortalMeeting(models.Model):
	section = models.ForeignKey(PortalSection)
	day = models.CharField(max_length=1)
	start = models.CharField(max_length=7)
	end	= models.CharField(max_length=7)
	room = models.ForeignKey(ClassRoom,blank=True,null=True)
	# Primary key
	class Meta:
		unique_together = ('section','day','start')

# R6
class Professor(models.Model):
	# Primary key
	name = models.CharField(max_length=32,primary_key=True) # name as listed on portal
	last_name = models.CharField(max_length=16)
	first_initial = models.CharField(max_length=16,blank=True,null=True)

# R7
class Teaches(models.Model):
	professor = models.ForeignKey(Professor)
	section = models.ForeignKey(PortalSection)
	class Meta:
		unique_together = ('professor', 'section', )

# R9
class Office(models.Model):
	building = models.ForeignKey(TeachingBuilding)
	room_no = models.CharField(max_length=32)
	class Meta:
		unique_together = ('building', 'room_no',)
		
# R8
class Works_At(models.Model):
	professor = models.ForeignKey(Professor)
	office = models.ForeignKey(Office)
	class Meta:
		unique_together = ('professor', 'office',)


# R10
class Book(models.Model):
	isbn = models.CharField(max_length=32,primary_key=True)
	image = models.CharField(max_length=128)
	title = models.CharField(max_length=128)
	author = models.CharField(max_length=64)
	edition = models.CharField(max_length=16)
	year = models.IntegerField(blank=True,null=True)
	publisher = models.CharField(max_length=128)

# R11
class Is_Textbook_For(models.Model):
	book = models.ForeignKey(Book)
	course = models.ForeignKey(PortalCourse)
	class Meta:
		unique_together = ('book', 'course',)

# R12
class BookCopy(models.Model):
	book = models.ForeignKey(Book)
	book_type = models.CharField(max_length=16,blank=True,null=True)
	buy_rent = models.CharField(max_length=8,blank=True,null=True)
	new_used = models.CharField(max_length=8,blank=True,null=True)
	price = models.DecimalField(max_digits=6,decimal_places=2)
	class Meta:
		unique_together = ('book','book_type','buy_rent','new_used')



##########
# Roster #
##########

# (R26)
class Dorm(Building):
	campus = models.CharField(max_length=32)

# R15
class DormRoom(models.Model):
	building = models.ForeignKey(Dorm)
	room_no = models.CharField(max_length=32)
	class Meta:
		unique_together = ('building', 'room_no',)

# R13
class Student(models.Model):
	email = models.CharField(max_length=64,primary_key=True)
	full_name = models.CharField(max_length=32)
	first_name = models.CharField(max_length=32)
	last_name = models.CharField(max_length=32)
	nickname = models.CharField(max_length=32)

# R14
class Roster(models.Model):
	student = models.ForeignKey(Student)
	semester = models.CharField(max_length = 16)
	class_code = models.CharField(max_length=4)
	room = models.ForeignKey(DormRoom,null=True,blank=True)
	room_phone = models.CharField(max_length=5,null=True,blank=True)
	cell_phone = models.CharField(max_length=12,null=True,blank=True)
	class Meta:
		unique_together = ('student','semester')

#########
# Sakai #
#########

# R20
class AppUser(models.Model):
    eid = models.CharField(max_length=64,primary_key=True)
    last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)
    time_inserted = models.DateTimeField(default=datetime.now, null=True, blank=True)
    f_processed = models.BooleanField()
    f_reviewed = models.BooleanField()
    def __unicode__(self):
		return self.eid

# R16
class SakaiUser(models.Model):
    eid = models.CharField(max_length=64,primary_key=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True,null=True)
    email = models.CharField(max_length=64, blank=True)
    time_inserted = models.DateTimeField(default=datetime.now, null=True, blank=True)
    contributor = models.ForeignKey(AppUser)
    roster_link = models.ForeignKey(Student, null=True, blank=True) # HMC Students Link
    portal_link = models.ForeignKey(Professor, null=True, blank=True)
    def __unicode__(self):
		return self.eid

# R17
class SakaiSite(models.Model):
	sid = models.CharField(max_length=64,primary_key=True)
	url = models.CharField(max_length=64,unique=True)
	campus = models.CharField(max_length=16,blank=True)
	discipline = models.CharField(max_length=64,blank=True)
	course_no = models.CharField(max_length=16,blank=True)
	course_sec = models.CharField(max_length=16,blank=True)
	semester = models.CharField(max_length=16,blank=True)
	time_inserted = models.DateTimeField(default=datetime.now, null=True, blank=True)
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)
	portal_link = models.ForeignKey(PortalCourse, null=True, blank=True) # Portal Course Link
	contributor = models.ForeignKey(AppUser)
	no_update = models.BooleanField()
	def __unicode__(self):
		return self.sid

# R18
class SakaiEnroll(models.Model):
	eid = models.ForeignKey(SakaiUser)
	sid = models.ForeignKey(SakaiSite)
	overall = models.IntegerField(null=True, blank=True)
	useful = models.IntegerField(null=True, blank=True)
	clear = models.IntegerField(null=True, blank=True)
	hard = models.IntegerField(null=True, blank=True)
	fun = models.IntegerField(null=True, blank=True)
	anonymous = models.BooleanField()
	role = models.CharField(max_length=32)
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)
	class Meta:
		unique_together = ('eid', 'sid',)

##########
# Review #
##########

# R21
class SakaiSiteReview(models.Model):
	user = models.ForeignKey(AppUser)
	sid = models.ForeignKey(SakaiSite)
	comments = models.TextField()
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)

# R23
class SakaiSiteCompare(models.Model):
	user = models.ForeignKey(AppUser)
	course_a = models.ForeignKey(SakaiSite, related_name="course_a")
	course_b = models.ForeignKey(SakaiSite, related_name="course_b")
	comments = models.TextField()
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)

# R22
class BookReview(models.Model):
	user = models.ForeignKey(SakaiUser)
	book = models.ForeignKey(Book)
	comments = models.TextField()
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)

# R24
class Sell(models.Model):
	eid = models.ForeignKey(SakaiUser)
	book = models.ForeignKey(Book)
	contact = models.CharField(max_length=64)
	condition = models.TextField()
	last_update = models.DateTimeField(default=datetime.now, null=True, blank=True)

