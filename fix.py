from main.models import *
for course in PortalCourse.objects.all():
	if len(course.program) > 2:
		course.course_no += course.program[0]
		course.program = course.program[1:]
		course.save()
