import mimetypes
import os
import time
from datetime import datetime
from io import BytesIO
import calendar
import pandas as pd
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import View
from django.db.models.signals import class_prepared
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from . import models
# from django.db import models
import json
from django.http import HttpResponse
from .forms import LoginForm
from .source.login import user_enrollment

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from main.models import Staff, Attendance, TimeSlot
from main.serializers import MainSerializer, AttendSerializer


@csrf_exempt
def staff_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        staffs = Staff.objects.all()
        serializer = MainSerializer(staffs, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MainSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def staff_detail(request, staff_id):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = MainSerializer(staff)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = MainSerializer(staff, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        staff.delete()
        return HttpResponse(status=204)


@csrf_exempt
def attendance_list(request):
	"""List all code snippets, or create a new snippet."""
	if request.method == 'GET':
		date_attendances = Attendance.objects.all()
		serializer = AttendSerializer(date_attendances, many=True)
		return JsonResponse(serializer.data, safe=False)

	elif request.method == 'POST':

		data = JSONParser().parse(request)
		if not data['in_time']:
			print('data base created')
		else:
			staff = Staff.objects.get(staff_id=data['staff'])
			designation = staff.designation
			print(designation)
			slot_time_in = datetime.strptime(str(staff.time_slot.time_slot_in), "%H:%M:%S")

			permission = datetime.strptime("01:00:00", "%H:%M:%S")
			time_zero = datetime.strptime("00:00:00", "%H:%M:%S")

			# time_mid = datetime.strptime("12:30:00", "%H:%M:%S")
			time_mid = datetime.strptime(str(TimeSlot.objects.get(staff__designation=designation).time_slot_mid), "%H:%M:%S")
			print(time_mid)
			print(datetime.strptime(data['in_time'], "%H:%M:%S"))
			print(data['in_time'])
			fn_time = slot_time_in - time_zero + permission

			fn_time_dif = fn_time - datetime.strptime(data['in_time'], "%H:%M:%S")
			fn_mid_time_dif = time_mid - datetime.strptime(data['in_time'], "%H:%M:%S")
			print(fn_time_dif)
			print(fn_mid_time_dif)

			if datetime.strptime(data['in_time'], "%H:%M:%S") < slot_time_in:
				data['forenoon_remarks'] = None
				data['afternoon_remarks'] = 'No Out'
			elif fn_time_dif.days >= 0:
				data['forenoon_remarks'] = 'Permission'
				data['afternoon_remarks'] = 'No Out'
			elif fn_mid_time_dif.days >= 0:
				data['forenoon_remarks'] = 'FN Leave'
				data['afternoon_remarks'] = 'No Out'
			else:
				data['forenoon_remarks'] = 'Full Day Leave FN'
				data['afternoon_remarks'] = 'No Out'

			# if data['total_remarks'] == 'leave':
			# 	print('data base created')


		print(data)
		serializer = AttendSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data, status=201)
		return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def attendance_detail(request, staff_id, date_id):
# Retrieve, update or delete a code snippet.
	try:
		date_attendance = Attendance.objects.get(staff_id=staff_id, date_id=date_id)
		staff = Staff.objects.get(staff_id=staff_id)
		designation = staff.designation
	except Attendance.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = AttendSerializer(date_attendance)
		return JsonResponse(serializer.data)

	elif request.method == 'PUT':
		data = JSONParser().parse(request)

		permission = datetime.strptime("01:00:00", "%H:%M:%S")
		time_two = datetime.strptime("02:00:00", "%H:%M:%S")
		time_mid = models.TimeSlot.objects.get(staff__designation=designation).time_slot_mid
		time_mid = datetime.strptime(str(time_mid), "%H:%M:%S")
		slot_time_out = datetime.strptime(str(staff.time_slot.time_slot_out), "%H:%M:%S")
		an_time = slot_time_out - time_two + permission
		an_time_dif = datetime.strptime(data['out_time'], "%H:%M:%S") - an_time

		if datetime.strptime(data['out_time'], "%H:%M:%S") > time_mid:
			if date_attendance.forenoon_remarks is None:
				if datetime.strptime(data['out_time'], "%H:%M:%S") > slot_time_out:
					data['afternoon_remarks'] = None
					data['total_remarks'] = None
				elif an_time_dif.days >= 0:
					data['afternoon_remarks'] = 'Permission'
					data['total_remarks'] = 'One Permission'
				else:
					data['afternoon_remarks'] = 'AN Leave'
					data['total_remarks'] = 'Half Day Leave'

			elif date_attendance.forenoon_remarks == 'Permission':
				if datetime.strptime(data['out_time'], "%H:%M:%S") > slot_time_out:
					data['afternoon_remarks'] = None
					data['total_remarks'] = 'One Permission'
				elif an_time_dif.days >= 0:
					data['afternoon_remarks'] = 'Permission'
					data['total_remarks'] = 'Two Permission'
				else:
					data['afternoon_remarks'] = 'AN Leave'
					data['total_remarks'] = 'Permission + Half Day Leave'

			elif date_attendance.forenoon_remarks == 'FN Leave':
				if datetime.strptime(data['out_time'], "%H:%M:%S") > slot_time_out:
					data['afternoon_remarks'] = None
					data['total_remarks'] = 'Half Day Leave'
				elif an_time_dif.days >= 0:
					data['afternoon_remarks'] = 'Permission'
					data['total_remarks'] = 'Half Day Leave + Permission'
				else:
					data['afternoon_remarks'] = 'AN Leave'
					data['total_remarks'] = 'Full Day Leave'
		else:
			data['total_remarks'] = None
			if datetime.strptime(data['out_time'], "%H:%M:%S") > slot_time_out:
				data['afternoon_remarks'] = None
				# data['total_remarks'] = 'Half Day Leave'
			elif an_time_dif.days >= 0:
				data['afternoon_remarks'] = None
				# data['total_remarks'] = 'Half Day Leave + Permission'
			else:
				data['afternoon_remarks'] = None
				# data['total_remarks'] = 'Full Day Leave'

		# else:
		# 	data['total_remarks'] = 'Special Case'
		# 	if datetime.strptime(data['out_time'], "%H:%M:%S") > slot_time_out:
		# 		data['afternoon_remarks'] = None
				# data['total_remarks'] = 'Half Day Leave'
			# elif an_time_dif.days >= 0:
			# 	data['afternoon_remarks'] = 'Permission'
				# data['total_remarks'] = 'Half Day Leave + Permission'
			# else:
			# 	data['afternoon_remarks'] = 'AN Leave'
				# data['total_remarks'] = 'Full Day Leave'

		# if data['out_time'] == 'No Out':
		# 	data['total_remarks'] = 'Special Case'


		if (data['in_time'] is None) and (data['out_time'] is None):
			data['total_remarks'] = 'Full Day Leave This'

		time_delta = datetime.strptime(data['out_time'], "%H:%M:%S") - datetime.strptime(data['in_time'], "%H:%M:%S")
		time_sec = time_delta.total_seconds()
		data['work_duration'] = time.strftime('%H:%M:%S', time.gmtime(time_sec))

		print(data)
		serializer = AttendSerializer(date_attendance, data=data)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data)
		return JsonResponse(serializer.errors, status=400)
	elif request.method == 'DELETE':
		date_attendance.delete()
		return HttpResponse(status=204)


# Create your views here.
# Utility functions -------------------------------------------------------------------------------
def dictfetchall(cursor):
	''' Return all rows from a cursor as a dict '''
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]


def dictfetchone(cursor):
	''' Return one row from a cursor as a dict '''
	columns = [col[0] for col in cursor.description]
	return dict(zip(columns, cursor.fetchone()))


# Homepage ----------------------------------------------------------------------------------------
def index(request):
	return render(request, 'main/base.html',
				  {
					  'page_title': 'Welcome',
				  })


# Login -------------------------------------------------------------------------------------------
def user_login(request):
	if request.method == 'POST':
		login_form = LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			return HttpResponseRedirect(request.GET.get('next', '/'))
		else:
			login_error = True
	else:
		login_form = LoginForm()
		login_error = False
	return render(request, 'main/login.html',
				  {
					  'login_form': login_form,
					  'login_error': login_error,
				  })


# Logout ------------------------------------------------------------------------------------------
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')


# Face Registration -------------------------------------------------------------------------------
@login_required
def user_face(request, staff_id):
	dept_id = models.Staff.objects.get(staff_id=staff_id).department_id
	dept_name = models.Department.objects.get(id=dept_id).name
	data_set = user_enrollment()
	left_data = json.dumps(data_set['Left'])
	right_data = json.dumps(data_set['Right'])
	center_data = json.dumps(data_set['Center'])
	one_entry = models.FaceData.objects.filter(staff_id=staff_id)
	left_facedata_all = {}
	if one_entry.count() == 0:
		models.FaceData.objects.create(staff_id=staff_id, left_data=left_data, right_data=right_data, center_data=center_data)
	else:
		models.FaceData.objects.filter(staff_id=staff_id).update(left_data=left_data, right_data=right_data, center_data=center_data)
	teachers = models.Staff.objects.filter(department_id=dept_id)
	facedatas = models.FaceData.objects.all()
	for facedata in facedatas:
		dic_data = {facedata.staff_id: facedata.staff_id}
		left_facedata_all.update(dic_data)

	return render(request, 'main/details/table.html',
					  {
						  'page_title': 'Staff Details',
						  'teachers': teachers,
						  'dept_name': dept_name,
						  'left_facedata_all': left_facedata_all.keys(),
					  })
	


# Details -----------------------------------------------------------------------------------------
def details(request):
	departments = models.Department.objects.all()
	return render(request, 'main/details/form.html',
				  {
					  'page_title': 'Staff details',
					  'departments': departments,
				  })

# Details -----------------------------------------------------------------------------------------
def attend_details(request):
	departments = models.Department.objects.all()

	months = []
	for i in range(1, 13):
		months.append([i, calendar.month_name[i]])
	dates = models.Date.objects.all()
	today = datetime.now().strftime('%Y-%m-%d')

	return render(request, 'main/results/form.html',
					  {
						  'page_title': 'Attendance Report',
						  'departments': departments,
						  'dates': dates,
						  'months': months,
						  'today': today,
					  })

def attend_details_list(request):
	''' View and edit details of teachers '''
	try:
		if request.method == 'POST':
			dept_id = request.POST['dept_name']
			get_date = request.POST['date']
			all_department = request.POST['department']
			month = request.POST['month']
			print(month)
			date_id = models.Date.objects.get(date=get_date).id
			dept_name = models.Department.objects.get(id=dept_id).name
			departments = models.Department.objects.all()
			teachers = models.Staff.objects.filter(department=dept_id, is_active=True)
			staffs = models.Staff.objects.filter(is_active=True)

			if month != '':
				if all_department == "True":
					attend_staffs = models.Attendance.objects.filter(date__date__month=month, staff__is_active=True).order_by('staff__department_id', 'staff_id', 'date__date', 'in_time')
					get_date = calendar.month_name[int(month)]
				else:
					attend_staffs = models.Attendance.objects.filter(date__date__month=month, staff__department_id=dept_id, staff__is_active=True).order_by('staff_id','date__date', 'in_time')
					get_date = calendar.month_name[int(month)]
			else:
				if all_department == "True":
					attend_staffs = models.Attendance.objects.filter(date=date_id, staff__is_active=True).order_by('staff__department_id', 'staff_id', 'in_time')
				else:
					attend_staffs = models.Attendance.objects.filter(date=date_id, staff__department_id=dept_id, staff__is_active=True).order_by('staff_id', 'in_time')

		else:
			return HttpResponseRedirect('/report/')

		# for attend_staff in attend_staffs:
			# print(attend_staff)
		return render(request, 'main/results/table.html',
					  {
						  'page_title': 'Staff Attendance Details',
						  'teachers': teachers,
						  'dept_name': dept_name,
						  'attend_staffs': attend_staffs,
						  'date': get_date,

					  })
	except ValueError:
		return HttpResponseRedirect('/report/')



def ab_attend_details(request):
	departments = models.Department.objects.all()

	# months = list(range(1, 13))
	months = []
	for i in range(1, 13):
		months.append([i, calendar.month_name[i]])
	dates = models.Date.objects.all()
	today = datetime.now().strftime('%Y-%m-%d')
	# with connection.cursor() as cursor:
	# 	cursor.execute("SELECT * FROM main_department")
	# 	departments = dictfetchall(cursor)
	# 	cursor.execute("SELECT * FROM main_date")
	# 	dates = dictfetchall(cursor)
	# 	# Dates = list(range(1, 9))
	return render(request, 'main/results/form.html',
					  {
						  'page_title': 'Absentee Report',
						  'departments': departments,
						  'dates': dates,
						  'months': months,
						  'today': today,
					  })

def ab_attend_details_list(request):
	''' View and edit details of teachers '''
	try:
		if request.method == 'POST':
			dept_id = request.POST['dept_name']
			# get_date = []

			get_date = request.POST['date']
			all_department = request.POST['department']
			month = request.POST['month']
			print(get_date)
			date_id = models.Date.objects.get(date=get_date).id

			dept_name = models.Department.objects.get(id=dept_id).name
			departments = models.Department.objects.all()
			teachers = models.Staff.objects.filter(department=dept_id)
			staffs = models.Staff.objects.filter(is_active=True)

			if month != '':
				if all_department == "True":
					attend_staffs = models.Attendance.objects.filter(date__date__month=month, staff__is_active=True).exclude(total_remarks='none').order_by('staff__department_id', 'staff_id', 'date__date', 'in_time')
				else:
					attend_staffs = models.Attendance.objects.filter(date__date__month=month, staff__department_id=dept_id, staff__is_active=True).exclude(total_remarks='none').order_by('staff_id','date__date', 'in_time')
			else:
				if all_department == "True":
					attend_staffs = models.Attendance.objects.filter(date=date_id, staff__is_active=True).exclude(total_remarks='none').order_by('staff__department_id', 'staff_id', 'in_time')
				else:
					attend_staffs = models.Attendance.objects.filter(date=date_id, staff__department_id=dept_id, staff__is_active=True).exclude(total_remarks='none').order_by('staff_id', 'in_time')

		else:
			return HttpResponseRedirect('/absent_report/')

		# for attend_staff in attend_staffs:
			# print(attend_staff)
		return render(request, 'main/results/table.html',
					  {
						  'page_title': 'Staff Absentee Details',
						  'teachers': teachers,
						  'dept_name': dept_name,
						  'attend_staffs': attend_staffs,
						  'date': date,

					  })
	except ValueError:
		return HttpResponseRedirect('/absent_report/')




def details_teachers(request):
	''' View and edit details of teachers '''
	try:
		if request.method == 'POST':
			dept_id = request.POST['dept_name']
			dept_name = models.Department.objects.get(id=dept_id).name
			teachers = models.Staff.objects.filter(department=dept_id)
		else:
			return HttpResponseRedirect('/details/')
		facedatas = models.FaceData.objects.all()
		left_facedata_all = {}
		for facedata in facedatas:
			dic_data = {facedata.staff_id: facedata.staff_id}
			left_facedata_all.update(dic_data)
		return render(request, 'main/details/table.html',
					  {
						  'page_title': 'Staff Details',
						  'teachers': teachers,
						  'dept_name': dept_name,
						  'left_facedata_all': left_facedata_all.keys(),
					  })
	except ValueError:
		return HttpResponseRedirect('/details/')


def profile_teacher(request, staff_id):
	facedatas = models.FaceData.objects.all()
	left_facedata_all = {}
	for facedata in facedatas:
		dic_data = {facedata.staff_id: facedata.staff_id}
		left_facedata_all.update(dic_data)
	try:
		if request.method == 'POST':
			staff_id = request.POST['staff_id']
			name = request.POST['name']
			designation = request.POST['designation']
			department_id = request.POST['dept_name']
			time_slot = request.POST['time_slot']
			dept_name = models.Department.objects.get(id=department_id).name
			one_entry = models.Staff.objects.filter(staff_id=staff_id)
			one_entry.update(name=name, department_id=department_id, designation_id=designation, is_active=True, time_slot_id=time_slot)
			# models.Staff.objects.update(staff_id=staff_id, name=name, department_id=dept_name, designation_id=designation, is_active=True, time_slot_id=time_slot)
			teachers = models.Staff.objects.filter(department_id=department_id)
			return render(request, 'main/details/table.html',
						  {
							  'page_title': 'Staff details',
							  'teachers': teachers,
							  'dept_name': dept_name,
							  'left_facedata_all': left_facedata_all.keys(),
						  })

		else:
			teacher = models.Staff.objects.get(staff_id=staff_id)
			departments = models.Department.objects.all()
			dept_name = teacher.department
			time_slots = models.TimeSlot.objects.all()

			designations = models.Designation.objects.all()
			if request.user.is_authenticated:
				url = 'main/details/profile.html'
			else:
				url = 'main/details/view_profile.html'
			return render(request, url,
						  {
							  'page_title': 'Staff Profile',
							  'profile': teacher,
							  'dept_name': dept_name,
							  'profile_type': 'teacher',
							  # 'dept_name': ''.join(dept_name),
							  'departments': departments,
							  'time_slots': time_slots,
							  'designations': designations

						  })
	except ValueError:
		return HttpResponseRedirect(f'/profile/teacher/{staff_id}/')



@login_required
def add_teacher(request):
	facedatas = models.FaceData.objects.all()
	# time_slots = models.TimeSlot.objects.all()
	left_facedata_all = {}
	for facedata in facedatas:
		dic_data = {facedata.staff_id: facedata.staff_id}
		left_facedata_all.update(dic_data)
	try:
		if request.method == 'POST':
			staff_id = request.POST['staff_id']
			name = request.POST['name']
			department_id = request.POST['dept_name']
			designation_id = request.POST['designation']
			time_slot_id = request.POST['time_slot']
			time_slots = models.TimeSlot.objects.all()
			dept_name = models.Department.objects.get(id=department_id).name
			models.Staff.objects.create(staff_id=staff_id, name=name, department_id=department_id, designation_id=designation_id, is_active=True, time_slot_id=time_slot_id)
			teachers = models.Staff.objects.filter(department_id=department_id)
			return render(request, 'main/details/table.html',
						  {
							  'page_title': 'Staff details',
							  'teachers': teachers,
							  'dept_name': dept_name,
							  'time_slots': time_slots,
							  'left_facedata_all': left_facedata_all.keys(),
						  })

		else:
			departments = models.Department.objects.all()
			staff_id = models.Staff.objects.latest("staff_id").staff_id
			time_slots = models.TimeSlot.objects.all()
			designations = models.Designation.objects.all()
			return render(request, 'main/details/profile.html',
						  {
							  'page_title': 'Add Staff',
							  'action': 'add_teacher',
							  'departments': departments,
							  'time_slots' : time_slots,
							  'designations' : designations,
							  'left_facedata_all': left_facedata_all.keys(),
							  'staff_id': staff_id
						  })
	except ValueError:
		return HttpResponseRedirect('/profile/teacher/add/')



@login_required
def delete_teacher(request):
	facedatas = models.FaceData.objects.all()
	left_facedata_all = {}
	for facedata in facedatas:
		dic_data = {facedata.staff_id: facedata.staff_id}
		left_facedata_all.update(dic_data)
	if request.method == 'POST':
		staff_id = request.POST['staff_id']
		dept_name = request.POST['dept_name']
		dept_id = models.Department.objects.get(name=dept_name).id
		models.Staff.objects.get(staff_id=staff_id, department_id=dept_id).delete()
		teachers = models.Staff.objects.filter(department_id=dept_id)
		return render(request, 'main/details/table.html',
					  {
						  'page_title': 'Staff details',
						  'teachers': teachers,
						  'dept_name': dept_name,
						  'left_facedata_all': left_facedata_all.keys(),
					  })
	else:
		return HttpResponseRedirect('/details/')


def date(request):
	date_attend = models.DateAttend.objects.all()
	dates = date_attend.filter(group__date_id=2)
	for date in dates:
		print(date.id)


# def download(request):
# 	return render(request, 'main/details/table.html')

# def download_as_excel(request):
# 	url = "http://127.0.0.1:8000/absent_report/teachers"

	# Assign the table data to a Pandas dataframe
	# table = pd.read_html(url)

	# Print the dataframe
	# print(table)
# Download Excel --------------------------------------------------------------------------------------
# def download_file(request):
# 	Define Django project base directory
	# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	# Define text file name
	# filename = 'Attendance_format1.xlsx'
	# Define the full file path
	# filepath = BASE_DIR + '/' + filename
	# filepath = BASE_DIR + '/'
	# Open the file for reading content
	# path = open(filepath, 'r')
	# path = open(filepath, 'r')
	# Set the mime type
	# mime_type, _ = mimetypes.guess_type(filepath)
	# Set the return value of the HttpResponse
	# response = HttpResponse(path, content_type=mime_type)
	# Set the HTTP header for sending to browser
	# response['Content-Disposition'] = "attachment; filename=%s" % filename
	# Return the response value
	# return response


# Attendance --------------------------------------------------------------------------------------
# def attendance(request):
# 	with connection.cursor() as cursor:
# 		cursor.execute("SELECT * FROM main_department")
# 		departments = dictfetchall(cursor)
# 		semesters = list(range(1, 9))
# 	return render(request, 'main/attendance/form.html',
# 				  {
# 					  'page_title': 'Attendance',
# 					  'departments': departments,
# 					  'semesters': semesters,
# 				  })
#
#
# def attendance_list(request):
# 	''' View attendance of students '''
# 	if request.method == 'POST':
# 		semester = request.POST['semester']
# 		dept_name = request.POST['dept_name']
# 		with connection.cursor() as cursor:
# 			cursor.execute(
# 				"SELECT * FROM main_student WHERE semester = %s AND dept_id = (SELECT dept_id FROM main_department WHERE name = %s)",
# 				[semester, dept_name])
# 			students = dictfetchall(cursor)
# 			cursor.execute(
# 				"SELECT name FROM main_subject WHERE semester = %s AND dept_id = (SELECT dept_id FROM main_department WHERE name = %s) ORDER BY subject_id",
# 				[semester, dept_name])
# 			subject_names = dictfetchall(cursor)
# 			attendance_list = []
# 			avg_list = []
# 			for student in students:
# 				cursor.execute(
# 					"SELECT student_id, attendance FROM main_classattendance WHERE student_id = %s ORDER BY subject_id",
# 					[student['student_id']])
# 				attendance = dictfetchall(cursor)
# 				attendance_list += attendance
# 				cursor.execute(
# 					"SELECT student_id, AVG(attendance) AS 'avg' FROM main_classattendance WHERE student_id = %s GROUP BY student_id",
# 					[student['student_id']])
# 				avg = dictfetchall(cursor)
# 				avg_list += avg
# 		return render(request, 'main/attendance/table.html',
# 					  {
# 						  'page_title': 'Attendance',
# 						  'students': students,
# 						  'subject_names': subject_names,
# 						  'attendance_list': attendance_list,
# 						  'avg_list': avg_list,
# 						  'dept_name': dept_name,
# 						  'semester': semester,
# 					  })
# 	else:
# 		return HttpResponseRedirect('/results/')
#
#
# # Results -----------------------------------------------------------------------------------------
# def results(request):
# 	with connection.cursor() as cursor:
# 		cursor.execute("SELECT * FROM main_department")
# 		departments = dictfetchall(cursor)
# 		# Dates = list(range(1, 9))
# 	return render(request, 'main/results/form.html',
# 				  {
# 					  'page_title': 'Results',
# 					  'departments': departments,
# 					  # 'semesters': semesters,
# 				  })
#
#
# def results_list(request):
# 	''' View results of students '''
# 	if request.method == 'POST':
# 		date = request.POST['date']
# 		dept_name = request.POST['dept_name']
# 		with connection.cursor() as cursor:
# 			cursor.execute(
# 				"SELECT * FROM main_staff WHERE is_active = True AND departemnt_id = (SELECT id FROM main_department WHERE name = %s)",
# 				[dept_name])
# 			# cursor.execute(
# 			# 	"SELECT * FROM main_student WHERE semester = %s AND dept_id = (SELECT dept_id FROM main_department WHERE name = %s)",
# 			# 	[semester, dept_name])
# 			staffs = dictfetchall(cursor)
# 			# students = dictfetchall(cursor)
# 			cursor.execute(
# 				"SELECT name FROM main_subject WHERE semester = %s AND dept_id = (SELECT dept_id FROM main_department WHERE name = %s) ORDER BY subject_id",
# 				[semester, dept_name])
# 			subject_names = dictfetchall(cursor)
# 			results_list = []
# 			avg_list = []
# 			for staff in staffs:
# 				cursor.execute("SELECT student_id, marks FROM main_marks WHERE student_id = %s ORDER BY subject_id",
# 							   [staff['student_id']])
# 				marks = dictfetchall(cursor)
# 				results_list += marks
# 				cursor.execute(
# 					"SELECT student_id, AVG(marks) AS 'avg' FROM main_marks WHERE student_id = %s GROUP BY student_id",
# 					[student['student_id']])
# 				avg = dictfetchall(cursor)
# 				avg_list += avg
#
# 		return render(request, 'main/results/table.html',
# 					  {
# 						  'page_title': 'Results',
# 						  'students': students,
# 						  'subject_names': subject_names,
# 						  'results_list': results_list,
# 						  'avg_list': avg_list,
# 						  'dept_name': dept_name,
# 						  'semester': semester,
# 					  })
# 	else:
# 		return HttpResponseRedirect('/results/')

#
# def render_to_pdf(template, context):
# 	template = get_template(template)
# 	html = template.render(context)
# 	result = BytesIO()
# 	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
# 	if not pdf.err:
# 		return HttpResponse(result.getvalue(), content_type='application/pdf')
# 	return None
#
#
# class GeneratePdf(View):
#     def get(self, request, *args, **kwargs):
#         obj = models.DateAttend.objects.get(id=1)
#         all = {
#             "Group": obj.group,
#             "In Time": obj.in_time,
#             "Out Time": obj.out_time,
#             "Work Duration": obj.work_duration,
#             "Remarks": obj.remarks,
#         }
#         pdf = render_to_pdf('base.html', all)
#         return HttpResponse(pdf, content_type='application/pdf')