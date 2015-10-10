from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext

from main.models import AppUser, SakaiUser, SakaiSite, SakaiEnroll, SakaiSiteReview, PortalCourse, PortalSection, Subject, Student, DormRoom, Dorm, Professor


import sys
sys.path.append("/home/emmatongjia/course-share.org/requests")
import requests
import re
import json
import datetime

from views_app import *
from views_form import *

def home(request):
	try:
		myeid = request.session["eid"]
		user = AppUser.objects.get(eid=myeid)
	except:
		return HttpResponseRedirect(reverse('main.views.login'))
	if not (user.f_processed and user.f_reviewed):
		return HttpResponseRedirect(reverse('main.views.rate'))
	return render_to_response('main/home.html')



def login(request):
	try:
		message = request.session["message"]
		request.session["message"] = None
	except:
		message = ""
	try:
		myeid = request.session["eid"]
		user = AppUser.objects.get(eid=myeid)
		return HttpResponseRedirect(reverse('main.views.home', args=()))
	except:
		return render_to_response('main/login.html', RequestContext(request, {'message':message}))


def logout(request):
	request.session["eid"] = ""
	return HttpResponseRedirect(reverse('main.views.login'))


def fn_validate(username, password):
	params = {'eid': username, 'pw': password, 'realm': '', 'submit': 'Login'}

	sess = requests.Session()
	r = sess.post("https://sakai.claremont.edu/portal/relogin", data=params)
	if (re.search('Alert:  Invalid login', r.text)):
		return False;
	try:
		appuser = AppUser.objects.get(eid=username)
	except:
		appuser = AppUser(eid=username)
	appuser.last_update = datetime.datetime.now()
	appuser.save()

	try:
		sakaiuser = SakaiUser.objects.get(eid=username)
	except:
		sakaiuser = SakaiUser(eid=username,contributor=appuser)
	sakaiuser.save()

	sess = requests.Session()

	m = re.search('icon-sakai-membership " href="(?P<addr>.*?)"',r.text)
	membership_url = m.group('addr')
	r = sess.post(membership_url, data=params)

	m = re.search(re.compile(r'<iframe.*?src="(?P<addr>.*?)"', re.DOTALL), r.text)
	membership_content_url = m.group('addr')
	r = sess.post(membership_content_url, data=params)

	site_urls = re.findall(re.compile(r'<h4><a href="(?P<addr>.*?)".*?>(?P<name>.*?)</a>', re.DOTALL), r.text)

	for (site_url,site_name) in site_urls:
		# Process site info
		r = sess.get(site_url.replace("/portal/","/direct/")+".json")
		try:
			site_json = json.loads(r.text)
			if (site_json['type'] != "course"):
				continue
			site_name = site_json['shortDescription']
			site_entityID = site_json['entityId']
		except KeyError:
			continue

		# Extract info
		site_lst = re.split(" |\n",site_name)
		# Insert into database
		try:
			new_site = SakaiSite.objects.get(sid=site_name)
		except:
			new_site = SakaiSite(sid=site_name,contributor=appuser)

		new_site.url = site_entityID
		new_site.save()

		try:
			s = SakaiEnroll.objects.filter(eid=sakaiuser,sid=new_site)[0]
		except:
			s = SakaiEnroll(eid=sakaiuser,sid=new_site,role="TBD")
		s.save()
	return True





def authenticate(request):
	if request.method != 'POST':
		return HttpResponseRedirect(reverse('main.views.login', args=()))

	# try:
	eid = request.POST['username']
	pwd = request.POST['password']
	realm = request.POST['realm']
	if len(realm) > 0:
		eid = eid.split('@')[0] + "@" + realm
	if fn_validate(eid, pwd):
		request.session["eid"] = eid
		request.session["pwd"] = pwd
		return HttpResponseRedirect(reverse('main.views.home', args=()))
	else:
		request.session['message'] = "Invalid Login"
		return HttpResponseRedirect(reverse('main.views.login', args=()))
	# except:
	# 	return HttpResponse("Unknown request.")

def process(request):
	try:
		username = request.session["eid"]
		password = request.session["pwd"]
		user = AppUser.objects.get(eid=username)
	except:
		return HttpResponse("You need to login.")
	params = {'eid': username, 'pw': password, 'realm': '', 'submit': 'Login'}
	
	sess = requests.Session()
	r = sess.post("https://sakai.claremont.edu/portal/relogin", data=params)
	if (re.search('Alert:  Invalid login', r.text)):
		return HttpResponse("Invalid login.")

	try:
		this_user = AppUser.objects.get(eid=username)
	except:
		this_user = AppUser(eid=username)
	this_user.save()

	sess = requests.Session()
	sess.post("https://courseshare.herokuapp.com/", data=params)
	m = re.search('icon-sakai-membership " href="(?P<addr>.*?)"',r.text)
	membership_url = m.group('addr')
	r = sess.post(membership_url, data=params)

	m = re.search(re.compile(r'<iframe.*?src="(?P<addr>.*?)"', re.DOTALL), r.text)
	membership_content_url = m.group('addr')
	r = sess.post(membership_content_url, data=params)

	site_urls = re.findall(re.compile(r'<h4><a href="(?P<addr>.*?)".*?>(?P<name>.*?)</a>', re.DOTALL), r.text)

	for (site_url,site_name) in site_urls:
		# Process site info
		r = sess.get(site_url.replace("/portal/","/direct/")+".json")
		try:
			site_json = json.loads(r.text)
			if (site_json['type'] != "course"):
				continue
			site_name = site_json['shortDescription']
			site_entityID = site_json['entityId']
		except KeyError:
			continue

		# Extract info
		site_lst = re.split(" |\n",site_name)
		# Insert into database
		try:
			new_site = SakaiSite.objects.get(sid=site_name)
		except:
			new_site = SakaiSite(sid=site_name,contributor=this_user)
		if not new_site.no_update:
			new_site.url = site_entityID
			new_site.campus = site_lst[0][:2]
			new_site.discipline = " ".join(site_lst[1:len(site_lst)-2])
			try:
				ind = site_lst[-2].index('.')
				new_site.course_no = site_lst[-2][:ind]
				new_site.course_sec = site_lst[-2][ind+1:]
			except:
				new_site.course_no = site_lst[-2]
			new_site.semester = site_lst[-1]
			new_site.save()
			####################
			## LINK TO PORTAL ##
			####################
			try:
				subject = Subject.objects.get(name=new_site.discipline)
				no = new_site.course_no
				if no[-1].isdigit():
					if len(no) < 3:
						no = "0"*(3-len(no))+no
				elif no[-2].isdigit():
					if len(no) < 4:
						no = "0"*(4-len(no))+no
				else:
					raise Exception("unable to process " + no)
				portal_course = PortalCourse.objects.get(subject=subject,course_no=no,semester=new_site.semester,program=new_site.campus)
				new_site.portal_link = portal_course
				new_site.save()
			except:
				pass
				# assert False,str(subject.code)+"--"+str(new_site.course_no)+"--"+str(new_site.semester)
		r = sess.post(site_url, data=params)
		# c
		m = re.search('icon-sakai-site-roster " href="(?P<addr>.*?)"',r.text)
		if not m:
			continue
		roster_url = m.group('addr')
		r = sess.post(roster_url, data=params)
		# c
		m = re.search(re.compile(r'<iframe.*?src="(?P<addr>.*?)"', re.DOTALL), r.text)
		roster_content_url = m.group('addr')
		r = sess.post(roster_content_url, data=params)
		# c
		m = re.findall('<tr><td>.*?mailto:.*?</td></tr>', r.text)
		if len(SakaiEnroll.objects.filter(sid=new_site)) == len(m):
			if (datetime.datetime.now() - new_site.last_update).days == 0:
				continue;
		for student_line in m:
			mm = re.search('<td>(?P<name>.*?)</td><td>(?P<eid>.*?)</td><td><a.*?>(?P<email>.*?)</a></td><td>(?P<role>.*?)</td>', student_line)
			if (mm.group('name')[0]=='<'):
				mm = re.search('<td><a.*?>(?P<name>.*?)</a></td><td>(?P<eid>.*?)</td><td><a.*?>(?P<email>.*?)</a></td><td>(?P<role>.*?)</td>', student_line)
			try:
				new_student = SakaiUser.objects.get(eid=mm.group('eid'))
			except:
				new_student = SakaiUser(eid=mm.group('eid'),contributor=this_user)
			names = mm.group('name').split(',')
			if len(names) == 1:
				first_name = names[0].strip()
				last_name = None
			else:
				assert len(names) == 2, names
				last_name,first_name = map(lambda x:x.strip(),names)
			new_student.first_name=first_name
			new_student.last_name=last_name
			new_student.email=mm.group('email').strip()
			####################
			## LINK TO ROSTER ##
			####################
			if new_student.eid[-4:]=="@hmc":
				try:
					roster_student = Student.objects.get(email=new_student.email)
					new_student.roster_link = roster_student
				except:
					pass
			####################
			## LINK TO Portal ##
			####################
			if mm.group('role') == "Instructor":
				try:
					professor = Professor.objects.filter(last_name=last_name)
					if len(professor) == 1:
						if not professor[0].first_initial or professor[0].first_initial==first_name[0]:
							new_student.portal_link = professor[0]
					elif len(professor) > 1:
						professor = professor.filter(first_initial=first_name[0])
						if professor: new_student.portal_link = professor[0]
				except:
					pass
			new_student.save()
			try:
				s = SakaiEnroll.objects.filter(eid=new_student,sid=new_site)[0]
				s.role=mm.group('role')
			except:
				s = SakaiEnroll(eid=new_student,sid=new_site,role=mm.group('role'))
			s.save()

		new_site = SakaiSite.objects.get(sid=site_name)
		new_site.last_update = datetime.datetime.now()
		new_site.save()


	user = AppUser.objects.get(eid=username);
	user.f_processed = True;
	user.save();
	return HttpResponse("ok")

def rate(request):
	try:
		myeid = request.session["eid"]
		user = AppUser.objects.get(eid=myeid)
	except:
		return HttpResponseRedirect(reverse('main.views.login', args=()))

	entries = SakaiEnroll.objects.filter(eid=myeid)
	if request.method == 'POST':
		for entry in entries:
			try:
				entry.overall = int(request.POST[entry.sid.url+"__overall"]);
			except:
				pass
			try:
				entry.useful = int(request.POST[entry.sid.url+"__useful"]);
			except:
				pass
			try:
				entry.clear = int(request.POST[entry.sid.url+"__clear"]);
			except:
				pass
			try:
				entry.hard = int(request.POST[entry.sid.url+"__hard"]);
			except:
				pass
			try:
				entry.fun = int(request.POST[entry.sid.url+"__fun"]);
			except:
				pass
			try:
				entry.anonymous = (request.POST[entry.sid.url+"__anonymous"] == "1");
			except:
				pass
			entry.save()
		user.f_reviewed = True;
		user.save();
		return HttpResponseRedirect(reverse('main.views.home', args=()))

	else:
		message = "" if user.f_processed else "process"
		return render_to_response('main/rate.html', RequestContext(request, 
			{'message':message,'roster':entries}))

