from main.models import Professor
for professor in Professor.objects.all():
	if professor.last_name == "" and professor.first_initial == "":
		instructor = professor.name
		groups = instructor.split(",")
		if len(groups) > 2:
			raise Exception("Professor "+instructor+" unable to process.")
		elif len(groups) == 2:
			prof_ln,prof_fn = groups
		else:
			if instructor[-2] == ' ':
				prof_ln = instructor[:-2]
				prof_fn = instructor[-1]
			elif instructor[-3] == ' ':
				prof_ln = instructor[:-3]
				prof_fn= instructor[-2]
			else:
				prof_fn = None
				prof_ln = instructor
		professor.last_name=prof_ln
		professor.first_initial=prof_fn
		professor.save()
