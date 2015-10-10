
import sys
sys.path.append("/home/course-share.org/requests")
import requests
import csv
import getpass
import re


from main.models import Subject,Building,TeachingBuilding,ClassRoom,PortalCourse,PortalSection,PortalMeeting,Professor,Book,Is_Textbook_For,BookCopy,Teaches


departments = {}
f = open("main/prepare/subjects.csv","rU")
for row in csv.reader(f):
	departments[row[0]]=row[1].strip()
	Subject(code=row[0].strip(),name=row[1].strip()).save()
f.close()


url_0="https://portal.claremontmckenna.edu/ics/Portlets/CRM/CXWebLinks/Portlet.CXFacultyAdvisor/CXFacultyAdvisorPage.aspx?SessionID={4e4ee664-797e-43ac-86bc-b508cd139b14}&MY_SCP_NAME=/cgi-bin/course/pccrscatarea.cgi&DestURL=http://cx-cmc.cx.claremont.edu:51081/cgi-bin/course/pccrslistarea.cgi?crsarea="
url_1="&yr="
url_2="&sess="
years=range(2002,2015)
years=[i for j in zip(years,years) for i in j]
years = map(str,years)
semesters=["SP","FA"]*15
params=zip(years,semesters)

def process(row):
	year,semester,coursecode,subject_name,section,instructors,enrollment,credit,campus,building,room,days,start,end,title,textbook = row
	
	# Final: Get PortalCourse object
	semester = semester + str(year)[-2:]
	try:
		portal_course = PortalCourse.objects.get(course_code=coursecode + " " + semester)
	except:
		print coursecode,semester,"not found"
		return
	try:
		portal_course.credit = credit
		portal_course.save()
	except:
		print coursecode,"nondecimal credit:",credit
	

# params = [("2013","FA")]
params = [("2013","FA"),("2014","SP"),("2014","FA")]
# start = False
for param in params:
	for department in departments.keys():
		# if department == "JAPN": start = True
		# if not start: continue
		department_name = departments[department]
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
			if row[7][:9] == "---------": 
				continue
			row.append("")
			if row[10] == "TBA": 
				row[10] = ""
			row[4] = param[0]
			row[6] = param[1]
			row.append(department_name)
			results.append(map(lambda x:row[x].strip(),[4,6,0,15,1,2,3,5,7,8,9,10,11,12,13,14]))
		# year,semester,coursecode,subject_name,section,instructors,
		# enrollment,credit,campus,building,room,days,start,end,title,textbook
		for i in range(1,len(results)):
			for j in range(len(results[i])):
				if (results[i][3] == "" or results[i][5] == "") and results[i][j] == "":
					results[i][j] = results[i-1][j]
		for result in results:
			process(result)
		print(param[0],param[1],department,"processed")


