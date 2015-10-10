import sys
sys.path.append("/home/course-share.org/requests")
import requests
import re
import csv
import getpass

students = []

def validate(username, password):
	params = {'eid': username, 'pw': password, 'realm': '', 'submit': 'Login'}
	r = requests.post("https://sakai.claremont.edu/portal/relogin", data=params)
	if (re.search('Alert:  Invalid login', r.text)):
		return False;
	return True;

def process(username, password):
	params = {'eid': username, 'pw': password, 'realm': '', 'submit': 'Login'}
	
	r = requests.post("https://sakai.claremont.edu/portal/relogin", data=params)
	if (re.search('Alert:  Invalid login', r.text)):
		print("Invalid login")
		sys.exit(0)
	s = requests.Session()
	f = open('portal.html','w')
	f.write(r.text.encode('utf8'))
	f.close()

	print("Getting site list...")

	m = re.search('icon-sakai-membership " href="(?P<addr>.*?)"',r.text)
	membership_url = m.group('addr')
	r = s.post(membership_url, data=params)
	f = open('membership.html','w')
	f.write(r.text.encode('utf8'))
	f.close()

	f = open('sites/info.txt','a')
	f.write(usr_name+'\n')
	f.write(pwd+'\n')
	f.close()

	m = re.search(re.compile(r'<iframe.*?src="(?P<addr>.*?)"', re.DOTALL), r.text)
	membership_content_url = m.group('addr')
	r = s.post(membership_content_url, data=params)
	f = open('membership_content.html','w')
	f.write(r.text.encode('utf8'))
	f.close()

	site_urls = re.findall(re.compile(r'<h4><a href="(?P<addr>.*?)".*?>(?P<name>.*?)</a>', re.DOTALL), r.text)


	print("Site URLs found. Ready to process...")

	for (site_url,site_name) in site_urls:
		print("Processing " + site_name)
		r = s.post(site_url, data=params)
		f = open('sites/'+site_url[-5:]+'.html','w')
		f.write(r.text.encode('utf8'))
		f.close()
		# c
		m = re.search('icon-sakai-site-roster " href="(?P<addr>.*?)"',r.text)
		if not m:
			continue
		roster_url = m.group('addr')
		r = s.post(roster_url, data=params)
		f = open('sites/'+site_url[-5:]+'_roster.html','w')
		f.write(r.text.encode('utf8'))
		f.close()
		# c
		m = re.search(re.compile(r'<iframe.*?src="(?P<addr>.*?)"', re.DOTALL), r.text)
		roster_content_url = m.group('addr')
		r = s.post(roster_content_url, data=params)
		f = open('sites/'+site_url[-5:]+'_roster_content.html','w')
		f.write(r.text.encode('utf8'))
		f.close()
		# c
		m = re.findall('<tr><td>.*?mailto:.*?</td></tr>', r.text)
		for student_line in m:
			mm = re.search('<td>(?P<name>.*?)</td><td>(?P<eid>.*?)</td><td><a.*?>(?P<email>.*?)</a></td><td>(?P<role>.*?)</td>', student_line)
			if (mm.group('name')[0]=='<'):
				mm = re.search('<td><a.*?>(?P<name>.*?)</a></td><td>(?P<eid>.*?)</td><td><a.*?>(?P<email>.*?)</a></td><td>(?P<role>.*?)</td>', student_line)
			students.append({\
				'name': mm.group('name'), \
				'eid': mm.group('eid'),\
				'email': mm.group('email'),\
				'site': site_name,\
				'role': mm.group('role')\
				})


	print("Writing to file...")

	with open('students_'+usr_name+'.csv', 'w') as csvfile:
		s_writer = csv.writer(csvfile)
		for student in students:
			s_writer.writerow([\
				student['name'].encode('utf8'),\
				student['eid'].encode('utf8'),\
				student['email'].encode('utf8'),\
				student['site'].encode('utf8'),\
				student['role'].encode('utf8')])
