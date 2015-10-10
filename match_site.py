
from main.models import Subject,SakaiSite, PortalCourse, PortalSection

for new_site in SakaiSite.objects.all():
	try:
		subject = Subject.objects.get(name=new_site.discipline)
		no = new_site.course_no
		if no[-1].isdigit():
			if len(no) < 3:
				no = "0"*(3-len(no))+no
		elif no[-2].isdigit():
			if len(no) < 4:
				no = "0"*(4-len(no))+no
		elif no[-3].isdigit():
			if len(no) < 5:
				no = "0"*(5-len(no))+no
		else:
			raise Exception("unable to process " + no)
		portal_course = PortalCourse.objects.get(subject=subject,course_no=no,semester=new_site.semester,program=new_site.campus)
		# section = new_site.course_sec
		# if len(section) == 1:
			# section = "0"+section
		# portal_section = PortalSection.objects.get(course=portal_course,section=section)
		# new_site.portal_link = portal_section
		new_site.portal_link = portal_course
		new_site.save()
		print "--",new_site.sid.replace("\n"," "),"SUCCEED."
	except:
		new_site.portal_link = None
		new_site.save()
		print "--",new_site.sid.replace("\n"," "),"FAIL."
		pass
