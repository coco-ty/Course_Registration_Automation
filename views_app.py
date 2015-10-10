from main.models import *
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext


import datetime

def sites(request,url=None):
	if not url:
		sites = SakaiSite.objects.all().order_by('discipline')
		return render_to_response('main/sakaisite_all.html', {'sites': sites})
	else:
		site = get_object_or_404(SakaiSite, url=url)
		roster = SakaiEnroll.objects.filter(sid=site).order_by('role', 'eid__last_name')
		return render_to_response('main/sakaisite.html', {'site': site, 'roster': roster})

def courses(request,code=None):
	if not code:
		courses_all = PortalCourse.objects.all()
		semester = request.GET.get('semester')
		title = request.GET.get('title')
		subject = request.GET.get('subject')
		if title:
			courses_all = courses_all.filter(title=title)
		elif subject:
			courses_all = courses_all.filter(subject__code=subject)
		else:
			if not semester: semester = "SP14"
			courses_all = courses_all.filter(semester=semester)
		return render_to_response('main/portalcourse_all.html', {'courses': courses_all})
	else:
		course = get_object_or_404(PortalCourse, course_code=" ".join(code.split("_")))
		sakaisites = SakaiSite.objects.filter(portal_link=course)
		sections = PortalSection.objects.filter(course=course)
		textbooks = Is_Textbook_For.objects.filter(course=course)
		return render_to_response('main/portalcourse.html',{'course': course, 'sections': sections, 'textbooks': textbooks, 'sites':sakaisites})

def sections(request,id):
	section = get_object_or_404(PortalSection, id=id)
	meetings = PortalMeeting.objects.filter(section=section)
	return render_to_response('main/portalsection.html',{'course': section.course, 'section': section, 'meetings': meetings})

def classrooms(request,id):
	room = get_object_or_404(ClassRoom, id=id)
	meetings = PortalMeeting.objects.filter(room = room)
	return render_to_response('main/classroom.html',{'room':room,'meetings':meetings})

def department(request,deptcode=None):
	if not deptcode:
		depts = Subject.objects.all().filter(portalcourse__semester='SP14').annotate(num_courses=Count('portalcourse')).order_by('-num_courses')
		return render_to_response('main/department_all.html', {'depts': depts})
	else:
		dept = get_object_or_404(Subject, code=deptcode)
		courses = PortalCourse.objects.filter(semester='SP14',subject=dept).order_by('course_no')
		return render_to_response('main/department.html',{'dept': dept, 'courses': courses})

def textbook(request,isbn):
	try:
		myeid = request.session["eid"]
		myuser = SakaiUser.objects.get(eid=myeid)
	except:
		return HttpResponseRedirect(reverse('main.views.login', args=()))
	book = get_object_or_404(Book,isbn=isbn)

	if request.method == 'POST':
		if request.POST["form"] == "review":
			mycomments = str(request.POST["comments"])
			book_id = Book.objects.get(isbn=isbn)
			new_review = BookReview(user=myuser,book=book_id,comments=mycomments)
			new_review.last_update = datetime.datetime.now()
			new_review.save();
		elif request.POST["form"] == "sell":
			mycontact = str(request.POST["contact"])
			mycondition = str(request.POST["condition"])
			book_id = Book.objects.get(isbn=isbn)
			# INSERT INTO Sell (eid, book, contact, condition)
			# VALUES (user, book_id, mycontact, mycondition)
			new_sale = Sell(eid=myuser,book=book_id,contact=mycontact,condition=mycondition)
			# UPDATE Sell
			# SET last_update=datetime.datetime.now()
			new_sale.last_update = datetime.datetime.now()
			new_sale.save();
	
	# SELECT * FROM Book WHERE isbn=textbookisbn
	textbook = get_object_or_404(Book, isbn=isbn)
	# SELECT * FROM BookCopy WHERE book=textbook ORDER BY price
	bookCopies = BookCopy.objects.filter(book=textbook).order_by('price')
	# SELECT * FROM Sell WHERE book=textbook
	studentCopies = Sell.objects.filter(book=textbook)
	# SELECT * FROM BookReview WHERE book=textbook
	studentReviews = BookReview.objects.filter(book=textbook)
	return render_to_response('main/textbook.html', RequestContext(request, {'textbook': textbook, 'bookCopies': bookCopies,
		'studentCopies': studentCopies, 'studentReviews': studentReviews}))

