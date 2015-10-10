import sys
sys.path.append("/home/course-share.org/requests")
import requests
import csv
import getpass
import re


from main.models import Building,TeachingBuilding,ClassRoom,PortalCourse,Professor,Teaches,Department,Works_For,Book,Is_Textbook_For,BookCopy,Dorm,DormRoom,CollegeRoster


url_0="https://portal.claremontmckenna.edu/ics/Portlets/CRM/CXWebLinks/Portlet.CXFacultyAdvisor/CXFacultyAdvisorPage.aspx?SessionID={4e4ee664-797e-43ac-86bc-b508cd139b14}&MY_SCP_NAME=/cgi-bin/course/pccrscatarea.cgi&DestURL=http://cx-cmc.cx.claremont.edu:51081/cgi-bin/course/pccrslistarea.cgi?crsarea="
url_1="&yr="
url_2="&sess="
years=range(2002,2015)
years=[i for j in zip(years,years) for i in j]
semesters=["SP","FA"]*15
params=zip(years,semesters)


departments = {}
f = open("subjects.csv","rU")
for row in csv.reader(f):
	departments[row[0]]=row[1]

f.close()

def format_time(ts):
	ampm = ts[-2:]
	[hour,minute] = ts[:-2].split(":")
	hour = int(hour)
	minute = int(minute)
	if ampm == "pm": hour += 12
	if hour == 12: hour = 0
	if hour == 24: hour = 12
	return hour + minute / 60.0



f_courses = open('courses.csv','w')
a_courses = csv.writer(f_courses, delimiter=",")

f_books = open('books.csv','w')
a_books = csv.writer(f_books, delimiter=",")
f_items = open('items.csv','w')
a_items = csv.writer(f_items, delimiter=",")



def process(row):
	global a_courses,a_books,a_items
	year,semester,coursecode,subject_name,section,instructors,enrollment,credit,campus,building,room,days,start,end,title,textbook = row
	if coursecode[2] == ' ':
		subject_code = coursecode[:2]
		rest = coursecode[3:]
	elif coursecode[3] == ' ':
		subject_code = coursecode[:3]
		rest = coursecode[4:]
	else:
		subject_code = coursecode[:4]
		rest = coursecode[4:]
	course_no = rest[:4].strip()
	suffix = rest[4:].strip()
	assert instructors[-4:] == "<br>"
	instructors = instructors[:-4].split("<br>")
	instructors = "|".join(instructors)
	try:
		seats_taken,seats = enrollment.split("/")
		seats_taken = int(seats_taken)
		seats = int(seats)
	except:
		seats_taken = 0
		seats = 0
	r = requests.get(textbook);
	content = r.text
	m = re.search("Required Material\(s\) \((.*?)\)",content)
	num_books = 0
	if not m:
		print "nothing here for",coursecode
	else:
		num_books = m.group(1)
		print num_books,"book(s) for",coursecode
		m = re.findall(re.compile('<h3 class="material-group-title">(.*?)\n.*?<span id="materialAuthor"><strong>Author:</strong> (.*?) <br/></span>.*?<span id="materialEdition"><strong>Edition:</strong> (.*?) <br/></span>.*?<span id="materialISBN"><strong>ISBN:</strong> (.*?)<br/></span>.*?<span id="materialCopyrightYear"><strong>Copyright Year:</strong> (.*?)<br/></span>.*?<span id="materialPublisher"><strong>Publisher:</strong> (.*?)<br/></span>.*?<div class="material-group-table">(.*?)<!-- End of material-group-details -->', re.DOTALL),content)
		for book in m:
			# title, author,edition,isbn,year,publisher,store
			a_books.writerow((coursecode,title)+book[:6])
			mm = re.findall(re.compile('Purchase</label></td>.*?<td>(.*?)&nbsp;.*?<td>(.*?)&nbsp;.*?<td>(.*?)&nbsp;.*?>\$(.*?)</td>', re.DOTALL),book[6])
			for entry in mm:
				a_items.writerow(book[:6]+entry)
	a_courses.writerow([year,semester,coursecode,title,subject_code,subject_name,course_no,suffix,section,instructors,seats_taken,seats,credit,campus,building,room,days,start,end,num_books])
	


params = [(2014,"SP")]
for param in params:
	for department in departments.keys():
		department_name = departments[department].strip()
		url = url_0 + department + url_1 + str(param[0]) + url_2 + param[1]
		r = requests.get(url);
		try:
			content = r.text[r.text.index("All Sections"):-1]
		except:
			print(param[0],param[1],department,"skipped")
			continue
		#
		content = content.replace("\t","").replace("\r","").replace("\n","")
		content = re.sub(" +"," ",content)
		content = content.replace("  "," ").replace("> ",">").replace(" <","<")
		content = content.replace(" >",">").replace("< ","<")
		#
		content = content.replace(" align=right","")
		content = content.replace(" align=left","")
		content = content.replace(" align=center","")
		content = content.replace("<td>","<td colspan=1>")
		m = re.findall('<tr class="glb_data_dark">(.*?)</td></tr>',content)
		results = [];
		for line in m:
			pieces = line.split("</td>")
			col = 0
			row = []
			for piece in pieces:
				mm = re.search("<td colspan=(.*?)>(.*?)$",piece)
				col_inc = int(mm.group(1))
				col_content = mm.group(2)
				row.append(col_content)
				row += [""]*(col_inc-1)
				col += col_inc
			#
			row.append("")
			#
			if row[10] == "TBA": 
				row[10] = ""
			#
			row[4] = param[0]
			row[6] = param[1]
			#
			if row[7][:9] == "---------": 
				row[7] = ""
			#
			mm = re.search("^(.*?)<a href='javascript:void\(\)' onClick='window.open\(\"(.*?)\".*?\)'>.*?</a>",row[13])
			if mm:
				row[13] = mm.group(1)
				row[14] = mm.group(2)
			#
			row.append(department_name)
			results.append(map(lambda x:row[x],[4,6,0,15,1,2,3,5,7,8,9,10,11,12,13,14]))
		#
		for i in range(1,len(results)):
			for j in range(len(results[i])):
				if results[i][j] == "":
					results[i][j] = results[i-1][j]
		for result in results:
			process(result)
		f_courses.flush()
		f_books.flush()
		f_items.flush()
			# if tuple[2].find("TBA</td>") != -1:
			# 	continue;
			# res = [department]
			# res.append(tuple[0])
			# res.append(tuple[1])
			# days = tuple[3]
			# for i in range(5):
			# 	res.append(1 if days[i]=="-" else 0)
			# res.append(format_time(tuple[4]))
			# res.append(format_time(tuple[5]))
			# a.writerow(res)
		print(param[0],param[1],department,"processed")




f_courses.close()
f_books.close()
f_items.close()
