from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.decorators import api_view
import tempfile
from django.contrib.auth import logout
from .serializers import BonafideModel
from .serializers import ExitSurvey
from io import BytesIO
from .models import Student
from .serializers import contactserialiser
from .serializers import Batchserialiser
from .serializers import internfeedback
from nocrest.models import Admins
from nocrest.models import Department
from nocrest.models import Application_table
from django.contrib.auth import authenticate
from nocrest.models import NoDues_application_table
from . import tuple_to_dict
import datetime
from rest_framework import status
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from django.db import connection, IntegrityError
from django.http.response import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import redirect
from rest_framework.response import Response
import random
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, EmailMessage
from xhtml2pdf import pisa
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import JsonResponse
from .models import Graduated
from django.core.mail import EmailMessage
from django.template.loader import get_template
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from datetime import datetime
media_root = settings.MEDIA_ROOT

from django.http import JsonResponse
import subprocess

def view_logs(request):
    log_file_path = '/var/www/html/webmits/.pm2/logs/noc-out.log'
    try:
        with open(log_file_path, 'r') as log_file:
            logs_content = log_file.read()
    except FileNotFoundError:
        logs_content = "Log file not found."
    return render(request, 'view_logs.html', {'logs_content': logs_content})

def trigger_pull(request):
    try:
        # Execute git pull command
        result = subprocess.run(['git', 'pull'], cwd='/var/www/html/webmits/Noc-main', capture_output=True, text=True)
        subprocess.run(['pm2', 'restart','noc'], cwd='/var/www/html/webmits/Noc-main', capture_output=True, text=True)
        return JsonResponse({'status': 'success', 'output': result.stdout})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def home(req):
  try:
    print(1)
    username = req.user.username
    email = req.user.email
    first_name = req.user.first_name
    # name = req.user.full_name
    last_name = req.user.last_name
    em = email[-13:]
    print(first_name)
    print(email)
    # print(name)
    print(username)
    
    if(em == 'mitsgl.a.in'):
        print("Tulla")
        q = "SELECT * FROM nocrest_student WHERE (Email = '{0}')".format(email)
        cursor = connection.cursor()
        cursor.execute(q)
        record = tuple_to_dict.ParseDictMultipleRecord(cursor)
        if(record):
            req.session['Enrollment'] = first_name
            return redirect("/api/studentlogin")
        else:
            return render(req, "Signup.html")
    # elif(em == 'itsgwalior.in'):
    else:
        q = "SELECT * FROM nocrest_admins WHERE email = '{0}'".format(email)
        req.session['Adminemail'] = email
        cursor = connection.cursor()
        cursor.execute(q)
        record = tuple_to_dict.ParseDictMultipleRecord(cursor)
        print("AAGELA")
        print(record[0]['Role'])
        if(record):
            req.session['Admincontact'] = record[0]['Contact']
            req.session['Adminname'] = record[0]['name']
            if(record[0]['Role']=='admin'):
                return redirect ('/api/superadmin')
            else:
                return redirect ('/api/adminDash')
        else:
            return render(req, "ADSignup.html")
  except Exception as e:
      print(e)
      return redirect('/')

def login(request):
    return render(request, 'Frontpage.html')
def custom_logout(request):
  try:
    logout(request)
    # Redirect to the front page or any other desired page
    return redirect('/')  # Replace 'frontpage' with the actual name or URL of your front page
  except Exception as e:
      print(e)

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Check if the uploaded file is an Excel file
        if not uploaded_file.name.endswith('.xlsx'):
            return JsonResponse({'status': 'Invalid file format. Please upload an Excel file.'}, status=400)

        # Read the Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)

        # Convert the DataFrame to a dictionary
        data_dict = df.to_dict(orient='records')

        # Now you can store the data_dict in the database
        for record in data_dict:
            # Assuming you have a model called YourModel
            Graduated.objects.create(**record)
            print(record)
        return JsonResponse({'status': 'File uploaded and data stored successfully'})
    else:
        return JsonResponse({'status': 'Invalid request'}, status=400)




@api_view(['GET','POST','DELETE'])
def Adsignup(req):
    return render(req, 'ADsignup.html')

@api_view(['GET','POST'])
def Frontpage(req):
    try:
        
        req.session['Admincontact'] = ''
        req.session['Adminpass'] = ''
        req.session['Adminemail'] = ''
        req.session['Enrollment'] = ''
        return render(req, "Frontpage.html")
    except Exception as e:
        print("Error",e)


@api_view(['GET','POST','DELETE'])
def Dashboard(req):
    try:
        return render(req, "Dashboard.html")
    except Exception as e:
        print("Error",e)

@api_view(['GET', 'POST', 'DELETE'])
def StudentLogin(req):
    try:
        print("KKKKk")
        if req.method == 'POST':
            if 'EnrollmentId' in req.POST and 'password' in req.POST:
                username = req.POST.get('EnrollmentId')
                password = req.POST.get('password')
                req.session['Enrollment'] = username
                q = "SELECT * FROM nocrest_student WHERE (username = '{0}' OR enrollmentid = '{0}') AND password = '{1}'".format(username, password)
                cursor = connection.cursor()
                cursor.execute(q)
                record = tuple_to_dict.ParseDictMultipleRecord(cursor)
                if record:
                    qr = "SELECT * FROM nocrest_graduated WHERE enrollmentid = '{0}'".format(username)
                    cursor2 = connection.cursor()
                    cursor2.execute(qr)
                    record2 = cursor2.fetchone()
                    if record2:
                        check = 1
                        qry = "SELECT * FROM nocrest_exitsurvey WHERE enrollmentid = '{0}'".format(username)
                        cursorn = connection.cursor()
                        cursorn.execute(qry)
                        recordn = cursorn.fetchone()
                        if(recordn):
                            check = 2
                    else:
                        check = 0
                else:
                    q = "SELECT * FROM nocrest_student WHERE (username = '{0}' OR enrollmentid = '{0}')".format(username)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(rec):
                        return render(req, "Frontpage.html",{"msg":'Incorrect Password'})
                    else:
                        return render(req, "Frontpage.html",{"msg":'Kindly Signup First'})
                qry = "select * from nocrest_department where Dep_Id = {0}".format(record[0]['Branch'])
                cursor = connection.cursor()
                cursor.execute(qry)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                return render(req, "Dashboard.html", {'record': record[0] ,"check": check,'branchstud':rec[0]['Department_name'] })
            else:
                return Response({'error': 'Missing username or password in the request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            username = req.session['Enrollment']
            # username = req.session['Enr']
            print("hello",username)
            q = "SELECT * FROM nocrest_student WHERE (username = '{0}' OR enrollmentid = '{0}')".format(username)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if record:
                    print(record)
                    qr = "SELECT * FROM nocrest_graduated WHERE enrollmentid = '{0}'".format(username)
                    cursor2 = connection.cursor()
                    cursor2.execute(qr)
                    record2 = cursor2.fetchone()
                    if record2:
                        check = 1
                    else:
                        check = 0
            else:
                return redirect('/')
            qry = "select * from nocrest_department where Dep_Id = {0}".format(record[0]['Branch'])
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            return render(req, "Dashboard.html", {'record': record[0] ,"check": check,'branchstud':rec[0]['Department_name'] })
    except Exception as e:
        print("Error", e)
        return redirect('/')


try:
    @csrf_exempt
    @api_view(['GET', 'POST', 'DELETE'])
    def StudentREg(req):
        print("Im in")
        try:
            if req.method == 'GET':
                username = req.GET.get('EnrollmentId')
                password = req.GET.get('password')
                req.session['StudPass'] = password
                req.session['Enrollment'] = username
                contact = contactserialiser(data=req.GET)
                print(contactserialiser)
                print(contact)
                if contact.is_valid():
                    print("Valid")
                    try:
                        contact.save()
                        print("Save successful")
                    except Exception as e:
                        print(f"Error during save: {e}")
                    print(f"Username: {username}, Password: {password}")
                    print("Hello")
                    return redirect("/api/studentlogin")
                else:
                    print(contact.errors)  # Print serializer errors for debugging
                    return Response(contact.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
except Exception as e:
            print("Error", e)

# @csrf_exempt
# @api_view(['GET', 'POST', 'DELETE'])
# def AdminREg(req):
#     try:
#         if req.method == 'GET':
#             contact = req.GET.get('Contact')
#             Password  = req.GET.get('Password')

#             # Continue with your existing logic
#             addata = Batchserialiser(data=req.GET)
#             print(Batchserialiser)
#             print(addata)
#             if addata.is_valid():
#                 name = addata.validated_data.get('name')
#                 contact = addata.validated_data.get('Contact')
#                 password = addata.validated_data.get('Password')
#                 print("Valid")
#                 try:
#                     # addata.name = req.GET.get('name')
#                     addata.save()
#                     print("Save successful")
#                 except Exception as e:
#                     print(f"Error during save: {e}")
#                 print(f"Username: {contact}, Password: {Password}")
#                 print("Hello")
#                 req.session['Admincontact'] = contact
#                 req.session['Adminpass'] = Password
#                 return redirect("/api/adminDash")
#             else:
#                 print(contact.errors)  # Print serializer errors for debugging
#                 return Response(contact.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         print("Error", e)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def AdminREg(req):
    try:
        if req.method == 'GET':
            role = req.GET.get('Role')
            Name = req.GET.get('name')
            email = req.GET.get('Email')
            Dept = req.GET.get('dept')
            contact = req.GET.get('Contact')
            password = req.GET.get('Password')
            stat = req.GET.get('status')
            print(role,Name, email, Dept, contact,password, stat )
            admindata = Batchserialiser(data=req.GET)
            
            if admindata.is_valid():
                admindata.save()
                print("Saved")
            else:
                return redirect('/')
            req.session['Admincontact'] = contact
            req.session['Adminpass'] = password
            return redirect("/api/adminDash")
        else:
                # Return errors if serializer is not valid
                return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("Error", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET','POST','DELETE'])
def Deptfp(req):
    try:
        req.session['Admincontact'] = ''
        req.session['Adminpass'] = ''
        req.session['Adminemail'] = ''
        q = "SELECT * FROM nocrest_admins"
        cursor = connection.cursor()
        cursor.execute(q)
        record = tuple_to_dict.ParseDictMultipleRecord(cursor)
        print(record)
        print('\n\n\n\n\n')
        q = "SELECT * FROM nocrest_application_table "
        cursor = connection.cursor()
        cursor.execute(q)
        record = tuple_to_dict.ParseDictMultipleRecord(cursor)
        print(record)

        return render(req, "Adminfp.html")
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def Tnpfp(req):
    try:
        return render(req, "Tnpfp.html")
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def DashLogin(req):
    print(22)
    try:
        if(req.session['Adminemail']):
            if(req.session['Adminemail'] == 'atul@mitsgwalior.in'):
                return redirect('/api/superadmin')
            contact = req.session['Admincontact']
            email = req.session['Adminemail']
            print(contact)
            print(email)
            if(contact):
                q = "SELECT * FROM nocrest_admins WHERE Contact = %s"
                cursor = connection.cursor()
                cursor.execute(q, [contact])
                print("HUIHUIHUI")
                record = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print(record)
            if(email):
                q = "SELECT * FROM nocrest_admins WHERE Email = %s "
                cursor = connection.cursor()
                cursor.execute(q, [email])
                print("HUIHUIHUI22")
                record = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print(record)
            if record:
                print("\n\n", record[0]['dept'])
                data = req.GET.get('clicked')
                print("data",data)
                if(data == 'None'):
                    data = 6
                if(record[0]['dept'] == 'Tnp'):
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'approved' and tnp_approval = ''"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print("count q",rec['count(*)'])
                    qry = "select count(*) from nocrest_application_table where tnp_approval = 'approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec2 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec2['count(*)'])
                    qry = "select count(*) from nocrest_application_table"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec3 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec3['count(*)'])
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec4 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec4['count(*)'])
                    print("kake bhai is here")
                    print(record[0]['Role'])
                    rrolee = record[0]['Role']
                    naemme = record[0]['name']
                    if(record[0]['status'] == 'passive'):
                        rec['count(*)'] = 0
                        rec2['count(*)'] = 0
                        rec3['count(*)'] = 0
                        rec4['count(*)'] = 0
                        return render (req, "AdminDash.html",{'count':rec['count(*)'],'count2':rec2['count(*)'],'count3':rec3['count(*)'],'count4':rec4['count(*)'],'clicked':data})
                    return render (req, "AdminDash.html",{'record':record[0],'count':rec['count(*)'],'count2':rec2['count(*)'],'count3':rec3['count(*)'],'count4':rec4['count(*)'],'clicked':data,'rrolee':rrolee,'naemme':naemme})

                else:
                    q = "select * from nocrest_department where department = '{0}'".format(record[0]['dept'])
                    cursor = connection.cursor()
                    cursor.execute(q)
                    rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    print(len(rec))
                    r = []
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept='{0}' and dept_approval = '' order by App_Date desc".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r += result
                    print(len(r))
                    r2 = []
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept='{0}' and dept_approval = 'approved' order by App_Date desc".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r2 += result
                    print(len(r2))
                    qry = "select count(*) from nocrest_application_table"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    print("HELLO0")
                    rec3 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec3['count(*)'])
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    print("HELLO1")
                    # print(cursor)
                    rec4 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec4['count(*)'])
                    r3 = []
                    print("HELLO3")
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved' and dept='{0}'".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r3 += result
                    print(len(r3))
                    print("HELLO4")
                    print(record[0]['Role'])
                    rrolee = record[0]['Role']
                    naemme = record[0]['name']
                    print(record)
                    if(record[0]['status'] == 'passive'):
                        print("huiiiii")
                        return render (req, "AdminDash.html",{'count':0,'count2':0,'count3':0,'count4':0,'count5':0,'clicked':data})
                    return render (req,"AdminDash.html",{'record':record[0],'count':len(r),'count2':len(r2),'count3':rec3['count(*)'],'count4':rec4['count(*)'],'count5':len(r3),'clicked':data,'rrolee':rrolee,'naemme':naemme})
            else:
                print("No record found")
                return JsonResponse({'error': 'No record found'}, status=404)
        else:
              return redirect('/api/adminfp')
    except Exception as e:
        print("Error", e)
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def DeptLogin(req):
    print(22)
    try:
        if req.method == 'POST':
            print(11)
            contact = req.POST.get('Contact')
            password = req.POST.get('password')
            print(contact)
            print(password)
            q = "SELECT * FROM nocrest_admins WHERE (Contact = %s OR email = %s) AND password = %s"
            cursor = connection.cursor()
            cursor.execute(q, [contact,contact, password])
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            # print(record['dept'])
            if record:
                print("\n\n", record[0]['dept'])
                req.session['Admincontact'] = record[0]['Contact']
                req.session['Adminemail'] = record[0]['Email']
            
                if(record[0]['dept'] == 'Tnp'):
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'approved' and tnp_approval = '' "
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec['count(*)'])
                    qry = "select count(*) from nocrest_application_table where tnp_approval = 'approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)Request
                    rec2 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec2['count(*)'])
                    qry = "select count(*) from nocrest_application_table"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec3 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec3['count(*)'])
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec4 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print("kake",rec4['count(*)'])
                    return redirect ('/api/adminDash')

                else:
                    q = "select * from nocrest_department where department = '{0}'".format(record[0]['dept'])
                    cursor = connection.cursor()
                    cursor.execute(q)
                    rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    print(len(rec))
                    r = []
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept='{0}' and dept_approval = '' order by App_Date desc".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r += result
                    print(len(r))
                    r2 = []
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept='{0}' and dept_approval = 'approved' order by App_Date desc".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r2 += result
                    print(len(r2))
                    qry = "select count(*) from nocrest_application_table"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    rec3 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec3['count(*)'])
                    qry = "select count(*) from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved'"
                    cursor = connection.cursor()
                    cursor.execute(qry)
                    # print(cursor)
                    rec4 = tuple_to_dict.ParseDictSingleRecord(cursor)
                    print(rec4['count(*)'])
                    r3 = []
                    for i in range(len(rec)):
                        m = rec[i]['id']
                        q = "select * from nocrest_application_table where dept_approval = 'Approved' and Tnp_approval = 'Approved' and dept='{0}'".format(m)
                        cursor = connection.cursor()
                        cursor.execute(q)
                        result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                        if(result):
                            print(i)
                            print("sample",result)
                            r3 += result
                    print(len(r3))
                    return redirect ('/api/adminDash')
            else:

                q = "SELECT * FROM nocrest_admins WHERE (Contact = '{0}' OR email = '{0}')".format(contact)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                if(rec):
                    return render(req, "Adminfp.html",{"msg":'Incorrect Password'})
                else:
                    return render(req, "Adminfp.html",{"msg":'Kindly Signup First'})
        return JsonResponse({'error': 'No record found'}, status=404)
    except Exception as e:
        print("Error", e)
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET','POST','DELETE'])
def SubmitApplication(req):
    try:
        print("Apply kaarne aa gaya hu ")
        if req.method == 'POST':
            name = req.POST.get('name')
            enrollmentid = req.POST.get('EnrollmentId')
            email = req.POST.get('Email')
            dept = req.POST.get('department')
            Year = req.POST.get('year')
            companyname = req.POST.get('companyname')
            Location = req.POST.get('location')
            Name_reciever = req.POST.get('name_reciever')
            designation_reciever = req.POST.get('Designation_reciever')
            Duration = req.POST.get('duration')
            StartDate = req.POST.get('startDate')
            EndDate = req.POST.get('endDate')
            Org_address = req.POST.get('org_address')
            Websitr_org = req.POST.get('websitr_org')
            Apply_through = req.POST.get('apply_through')
            Stipend = req.POST.get('stipend')
            if 'offerletter' in req.FILES:
                offerLetter_file = req.FILES['offerletter']
            else:
                offerLetter_file = None 
            print(offerLetter_file)
            Declaration = req.POST.get('declaration')
            appid=name[1]+name[2]+str(random.randint(100000,9999999))
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            current_time = current_datetime.time()
            print(current_date, current_time)
            current_date_str = current_datetime.strftime("%Y-%m-%d")
            current_time_str = current_datetime.strftime("%H:%M:%S")
            dateapp = current_date_str
            time = current_time_str
            contactdata = Application_table(
                Name=name,
                EnrollmentId=enrollmentid,
                Email=email,
                dept=dept,
                year=Year,
                Company=companyname,
                location = Location,
                name_reciever = Name_reciever,
                Designation_reciever = designation_reciever,
                duration = Duration,
                startDate = StartDate,
                endDate = EndDate,
                org_address = Org_address,
                websitr_org =Websitr_org,
                apply_through = Apply_through,
                offerletter = offerLetter_file,
                stipend = Stipend,
                declaration =Declaration,
                App_Id=appid,
                App_Date=dateapp,
                App_time=time,
            )
            contactdata.save()
            try:
             current_directory = os.getcwd()
             html_template = get_template(os.path.join(current_directory,'nocrest/Static/emailnoc.html'))
            except Exception as error:
                return HttpResponse(error)
            try:
                context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                html_content = html_template.render(context)
                subject = 'Testing'
                message = 'Successfully applied for NO Dues'
                from_email = 'suyashu1606.agarwal@gmail.com'
                recipient_list = [email]
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.content_subtype = "html"
                email.body = html_content
                email.send()
                print("Mail Sent")
            except Exception as email_exception:
                print("Email sending failed:", email_exception)
                return HttpResponse(email_exception)
            return render(req, "Dashboard.html", {'message': 'ok'})
        else:
            return HttpResponse("Method not allowed", status=405)
    except Exception as e:
        print("Error:", e)
        return HttpResponse("An error occurred", status=500)



@api_view(['GET','POST','DELETE'])
def ApplyBonafide(req):
    try:
        print("Hello")
        if req.method == 'POST':
            print("hola amigos")
            Name = req.POST.get('student_name')
            Enroll = req.POST.get('EnrollmentId')
            f_name = req.POST.get('fathers_name')
            sem = req.POST.get('Semester')
            Email = req.POST.get('email')
            session = req.POST.get('session')
            dept = req.POST.get('Branch')
            current_datetime = datetime.now()
            date = current_datetime.date()
            bonafidedata = BonafideModel(
                student_name = Name,
                EnrollmentId = Enroll,
                fathers_name = f_name,
                Semester = sem,
                email = Email,
                session = session,
                application_date = date,
                Branch = dept,
            )
            bonafidedata.save()
            current_directory = os.getcwd()
            html_template = get_template(os.path.join(current_directory,'nocrest/Static/Appliedbonaf.html'))
            context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
            html_content = html_template.render(context)
            subject = 'Testing'
            message = 'Successfully applied for NO Dues'
            from_email = 'suyashu1606.agarwal@gmail.com'
            recipient_list = [Email]
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.content_subtype = "html"
            email.body = html_content
            email.send()
            print("Mail Sent")
            print("Application data Saved")
            return render(req, "Dashboard.html", {'message': 'ok'})
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def SubmitNoDuesApp(req):
    try:
        if req.method == 'POST':
            enr = req.POST.get('EnrollmentId')
            print(enr)
            print(1111111)
            q = "select * from nocrest_NoDues_application_table where EnrollmentId = '{0}'  order by App_Date desc".format(enr)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(records):
                print("MESiiiiiiiiiiiiii")
                return render(req, "Dashboard.html", {'message': 'error'})

                # Get the data from the POST request
            else:
                print(1234)
                name = req.POST.get('name')
                enrollmentid = req.POST.get('EnrollmentId')
                email = req.POST.get('Email')
                dept = req.POST.get('department')
                apply = req.POST.get('apply')
                current_datetime = datetime.datetime.now()
                current_date = current_datetime.date()
                current_time = current_datetime.time()
                print(current_date, current_time)
                current_date_str = current_datetime.strftime("%Y-%m-%d")
                current_time_str = current_datetime.strftime("%H:%M:%S")
                dateapp = current_date_str
                time = current_time_str
                # Create an instance of Application_table
                contactdata = NoDues_application_table(
                    Name=name,
                    EnrollmentId=enrollmentid,
                    Email=email,
                    dept=dept,
                    App_Id=apply,
                    App_Date=dateapp,
                    App_time=time
                )
                # Save the instance to the database
                contactdata.save()
                # send_mail(
                #     'Testing',
                #     'Successfully applied for NO Dues',
                #     'suyashu1606.agarwal@gmail.com',
                #     [email],
                #     fail_silently=False
                # )
                current_directory = os.getcwd()
                html_template = get_template(os.path.join(current_directory,'nocrest/Static/emailnodues.html'))
# Render the template with any context variables you want to include
                context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                html_content = html_template.render(context)
# Create the EmailMessage object
                subject = 'Testing'
                message = 'Successfully applied for NO Dues'
                from_email = 'your_email@gmail.com'  # Sender's email address
                recipient_list = [email]  # List of recipient email addresses
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.content_subtype = "html"  # Set the content type to HTML
                email.body = html_content
# Send the email
                email.send()
                return render(req, "Dashboard.html", {'message': 'ok'})
    except Exception as e:
        print("Error", e)
        return render(req, "Frontpage.html")
    
@api_view(['GET', 'POST'])
def ExitSurveySubmit(req):
    try:
        if req.method == 'POST':
            enr = req.POST.get('EnrollmentId')
            print(enr)
            q = "SELECT * FROM nocrest_NoDues_application_table WHERE EnrollmentId = '{0}' ORDER BY App_Date DESC".format(enr)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            
            if records:
                return render(req, "Dashboard.html", {'message': 'error'})
            else:
                # Extract data from POST request
                name = req.POST.get('name')
                enrollmentid = req.POST.get('EnrollmentId')
                email = req.POST.get('Email')
                department = req.POST.get('department')
                phone = req.POST.get('mobile')
                apply = req.POST.get('apply')

                dob = req.POST.get('dob')
                gender = req.POST.get('gender')
                course = req.POST.get('course')
                branch = req.POST.get('branch')
                rate_faculty = req.POST.get('rate_faculty')
                teaching_methods = req.POST.get('teaching_methods')
                learning_resources = req.POST.get('learning_resources')
                syllabus_completion = req.POST.get('syllabus_completion')
                course_relevance = req.POST.get('course_relevance')
                teacher_preparedness = req.POST.get('teacher_preparedness')
                course_outcomes = req.POST.get('course_outcomes')
                soft_skills = req.POST.get('soft_skills')
                internships_support = req.POST.get('internships_support')
                student_orgs = req.POST.get('student_orgs')
                curricular_extracurricular = req.POST.get('curricular_extracurricular')
                quizzes = req.POST.get('quizzes')
                evaluation_fairness = req.POST.get('evaluation_fairness')
                library_resources = req.POST.get('library_resources')
                curriculum_flexibility = req.POST.get('curriculum_flexibility')
                nptel_moocs = req.POST.get('nptel_moocs')
                full_semester_internship = req.POST.get('full_semester_internship')
                training_placement = req.POST.get('training_placement')
                sports_facilities = req.POST.get('sports_facilities')
                hostel_maintenance = req.POST.get('hostel_maintenance')
                overall_rating = req.POST.get('overall_rating')
                final_feedback = req.POST.get('final_feedback')

                current_datetime = datetime.now()
                current_date_str = current_datetime.date()
                current_time_str = current_datetime.time()

                # Save the data to the database
                survey_data = ExitSurvey(
                    Name=name,
                    EnrollmentId=enrollmentid,
                    Email=email,
                    Department=department,
                    Phone=phone,
                    Apply=apply,
                    DOB=dob,
                    Gender=gender,
                    Course=course,
                    Branch=branch,
                    RateFaculty=rate_faculty,
                    TeachingMethods=teaching_methods,
                    LearningResources=learning_resources,
                    SyllabusCompletion=syllabus_completion,
                    CourseRelevance=course_relevance,
                    TeacherPreparedness=teacher_preparedness,
                    CourseOutcomes=course_outcomes,
                    SoftSkills=soft_skills,
                    InternshipsSupport=internships_support,
                    StudentOrgs=student_orgs,
                    CurricularExtracurricular=curricular_extracurricular,
                    Quizzes=quizzes,
                    EvaluationFairness=evaluation_fairness,
                    LibraryResources=library_resources,
                    CurriculumFlexibility=curriculum_flexibility,
                    NPTELMOOCs=nptel_moocs,
                    FullSemesterInternship=full_semester_internship,
                    TrainingPlacement=training_placement,
                    SportsFacilities=sports_facilities,
                    HostelMaintenance=hostel_maintenance,
                    OverallRating=overall_rating,
                    FinalFeedback=final_feedback,
                    AppDate=current_date_str,
                    AppTime=current_time_str
                )
                survey_data.save()
                # Prepare and send the email
                # current_directory = os.getcwd()
                # html_template = get_template(os.path.join(current_directory, 'nocrest/Static/emailnodues.html'))
                # context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                # html_content = html_template.render(context)
                # subject = 'Exit Survey Submission Confirmation'
                # message = 'Thank you for submitting the exit survey. Your responses have been recorded successfully.'
                # from_email = 'your_email@gmail.com'  # Sender's email address
                # recipient_list = [email]  # List of recipient email addresses
                # email = EmailMessage(subject, message, from_email, recipient_list)
                # email.content_subtype = "html"  # Set the content type to HTML
                # email.body = html_content
                # email.send()
                return render(req, "Dashboard.html", {'message': 'ok'})
    except Exception as e:
        print("Error", e)
        return render(req, "Frontpage.html")

@api_view(['GET','POST','DELETE'])
def ShowAppliedstudent(req):
    try:
         if req.session['Adminemail'] == '':
             print("session khali")
             return redirect('/')
         elif req.method == 'GET':
            department = req.GET.get('dept')
            print(req.GET.get('dept'))
            rec = []
            if(department != 'Tnp'):
                qry = "select * from nocrest_department where Department = '{0}'".format(department)
                cursor = connection.cursor()
                cursor.execute(qry)
                records = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print("xxxxxxxxxx",records)
                print(len(records))
                for i in range(0,len(records)):
                    m = records[i]['id']
                    q = "select * from nocrest_application_table where dept='{0}' and Dept_approval='' order by App_Date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                        print(i)
                        print("sample",result)
                        rec += result
                return JsonResponse(rec,safe=False)
            print("\n\n\n",rec)
            if(department == 'Tnp'):
                q = "select * from nocrest_application_table where Dept_approval='Approved' and Tnp_approval = '' order by App_Date desc "
                print(q)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print("xxxxxxxxxx",rec)
            # if(rec):
                return JsonResponse(rec,safe=False)
            # else:
            #     return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)


@api_view(['GET','POST','DELETE'])
def NoDuesAppliedstudent(req):
    try:
         if req.method == 'GET':
            department = req.GET.get('dept')
            print("fnjbqiughienbijnbiuehgiugnigbiu",department)
            if(department == 'Tnp'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(department)
            elif(department == 'Hostel'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(department)
            elif(department == 'Lib'):
                de = department +"_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(de)
            elif( department == 'acc'):
                department+="_approval"
                q = "SELECT * FROM nocrest_NoDues_application_table WHERE (dept_approval = 'approved' AND Tnp_approval = 'approved' AND hostle_approval = 'approved' AND lib_approval = 'approved' AND Acc_approval = '')  order by App_Date desc"
                print(q)

            else:
                q = "select * from nocrest_NoDues_application_table where dept='{0}' and Dept_approval=''  order by App_Date desc".format(department)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            if(records):
                return JsonResponse(records,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)


@api_view(['GET','POST','DELETE'])
def AppliedStudeApproved(req):
    try:
         if req.session['Adminemail'] == '':
             return redirect('/')
         if req.method == 'GET':
            department = req.GET.get('dept')
            print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",department)
            apr = 'Approved'
            if(department == 'Tnp'):
                q = f"select * from nocrest_application_table where Dept_approval='{apr}' and {department}_approval ='Approved'  order by App_Date desc"
                print(q)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                return JsonResponse(rec,safe=False)
            else:
                q = "select * from nocrest_department where department = '{0}'".format(department)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print(len(rec))
                r = []
                for i in range(len(rec)):
                    m = rec[i]['id']
                    q = "select * from nocrest_application_table where dept='{0}' and dept_approval = 'approved' order by App_Date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                            print(i)
                            r += result
                            print(r)
                print("\n\n\n\n\n\n",len(r))
            if(r):
                return JsonResponse(r,safe=False)
            else:
                return redirect('/')
    except Exception as e:
        print("Error", e)
@api_view(['GET','POST','DELETE'])
def AppliedDisapprovedStud(req):
    try:
         if req.session['Adminemail'] == '':
             return redirect('/')
         if req.method == 'GET':
            department = req.GET.get('dept')
            print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",department)
            apr = 'Approved'
            if(department == 'Tnp'):
                q = f"select * from nocrest_application_table where Dept_approval='{apr}' and tnp_approval ='Declined'  order by App_Date desc"
                print(q)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                return JsonResponse(rec,safe=False)
            else:
                q = "select * from nocrest_department where department = '{0}'".format(department)
                cursor = connection.cursor()
                cursor.execute(q)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print(len(rec))
                r = []
                for i in range(len(rec)):
                    m = rec[i]['id']
                    q = "select * from nocrest_application_table where dept='{0}' and dept_approval = 'declined' order by App_Date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                        print(i)
                        print("sample",result)
                        r += result
                print(r)

            if(r):
                return JsonResponse(r,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)

@api_view(['GET','POST','DELETE'])
def NDapproved(req):
    try:
         if req.method == 'GET':
            department = req.GET.get('dept')
            print("fnjbqiughienbijnbiuehgiugnigbiu",department)
            if(department == 'Tnp'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = 'approved'  order by App_Date desc".format(department)
            elif(department == 'Hostel'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = 'approved'  order by App_Date desc".format(department)
            elif(department == 'Lib'):
                de = department +"_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = 'approved'  order by App_Date desc".format(de)
            elif( department == 'acc'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = 'approved'  order by App_Date desc".format(department)
            elif( department == 'Exam'):
                department+="_approval"
                q = "select * from nocrest_NoDues_application_table where {0} = 'approved'  order by App_Date desc".format(department)
            else:
                q = "select * from nocrest_NoDues_application_table where dept='{0}' and Dept_approval='approved'  order by App_Date desc".format(department)
                print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            if(records):
                return JsonResponse(records,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)



@api_view(['GET','POST','DELETE'])
def ChekPreviousApp(req):
    print(1111)
    try:
         if req.session['Enrollment'] == '':
                return redirect('/')
         if req.method == 'GET':
            username = req.session['Enrollment']
            print("Session",req.session['Enrollment'],"\n\n")
            q="select Email from nocrest_student where EnrollmentId='{0}' ".format(username)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictSingleRecord(cursor)

            email=records['Email']
            print(email)

            q = "select * from nocrest_application_table where email='{0}'  order by App_Date desc, App_time desc".format(email)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            if(records):
                return JsonResponse(records,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)

        
@api_view(['GET','POST','DELETE'])
def BonafStatus(req):
    print(1111)
    try:
         if req.session['Enrollment'] == '':
                return redirect('/')
         if req.method == 'GET':
            username = req.session['Enrollment']
            print("Session",req.session['Enrollment'],"\n\n")
            q="select Email from nocrest_student where EnrollmentId='{0}' ".format(username)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictSingleRecord(cursor)

            email=records['Email']
            print(email)

            q = "select * from nocrest_bonafidemodel where email='{0}'  order by application_date desc".format(email)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            if(records):
                return JsonResponse(records,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)


@api_view(['GET','POST','DELETE'])
def ShowGradStuds(req):
    print(1111)
    try:
         if req.method == 'GET':


            q="select * from nocrest_graduated "
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(records)
            if(records):
                return JsonResponse(records,safe=False)

    except Exception as e:
        print("Error", e)

@api_view(['GET','POST','DELETE'])
def NoduesStatus(req):
    print(1111)
    try:
         if req.method == 'GET':
            enr = req.GET.get('EnrollmentId')
            print("fnjbqiughienbijnbiuehgiugnigbiu",enr)

            q="select * from nocrest_nodues_application_table where EnrollmentId='{0}' order by App_Date desc".format(enr)
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictSingleRecord(cursor)

            print("xxxxxxxxxx",records)
            if(records):
                return JsonResponse(records,safe=False)
            else:
                return render(req,"Dashboard.html")
    except Exception as e:
        print("Error", e)




@api_view(['GET', 'POST', 'DELETE'])
def EditApplication(req):
    try:
        if req.method =='POST':
            print(req.POST['id'])
            print(req.POST['dept'])
            print(req.POST['contact'])
            contact = req.POST['contact']
            dept = req.POST['dept']
            studept = req.POST['studept']
            q = "select * from nocrest_application_table where id={0}".format(req.POST['id'])
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(record)
            return render(req, 'Applicationedit.html', {'data': record, 'dept': dept, 'contact': contact})
    except Exception as e:
        print(e)

@api_view(['GET','POST','DELETE'])
def NDApplicationedit(req):
    try:
        if req.method =='GET':
            print(req.GET['id'])
            print(req.GET['dept'])
            dept = req.GET['dept']
            q="select * from nocrest_nodues_application_table where id={0}".format(req.GET['id'])
            cursor=connection.cursor()
            cursor.execute(q)
            record=tuple_to_dict.ParseDictSingleRecord(cursor)
            return render(req,'NDApplicationedit.html',{'data':record,'dept':dept})
    except Exception as e:
        print(e)

@api_view(['GET','POST','DELETE'])
def EditFAculty(req):
    try:
        if req.method =='GET':
            print(req.GET['id'])
            q="select * from nocrest_admins where id={0}".format(req.GET['id'])
            cursor=connection.cursor()
            cursor.execute(q)
            record=tuple_to_dict.ParseDictSingleRecord(cursor)
            return render(req,'Facultyedit.html',{'data':record})
    except Exception as e:
        print(e)

import qrcode
@api_view(['GET', 'POST', 'DELETE'])
def EditSaveDept(request):
    try:
        if request.method == 'POST':
            print(1111)
            department = request.POST.get('randomdept')
            print("v hjbvuafvb dfjbvb", department)
            print(request.POST.get('idbb'))
            Name = request.POST.get('name_reciever')
            designation = request.POST.get('Designation_reciever')
            company = request.POST.get('Company')
            today_date = datetime.now().date()
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            stud_name = request.POST.get('Name')
            stud_enr = request.POST.get('EnrollmentId')
            stud_branch = request.POST.get('dept')
            location = request.POST.get('location')
            approval = request.POST.get('approval')
            comment = request.POST.get('comment')
            approveerole = request.POST.get('role')
            approveename = request.POST.get('name')
            print(approveerole)
            print(approveename)
            approved_by = approveerole+'_'+approveename
            print(approved_by)
            print(approval, comment)
            qry = "select * from nocrest_department where Dep_Id = '{0}'".format(6)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(rec[0]['Department_name'])
            stud_branch = rec[0]['Department_name']
            print(Name, designation, company, start_date, end_date, stud_branch, stud_name, stud_enr)
            e_mail = request.POST['Email']
            apr_time = datetime.now()
            print(e_mail)
            print(apr_time)
            q="select count(*) from nocrest_application_table where tnp_approval = 'approved'"
            cursor=connection.cursor()
            cursor.execute(q)
            record=tuple_to_dict.ParseDictSingleRecord(cursor)
            apid = record['count(*)'] + 1
            print(record['count(*)'])
            if department == 'Tnp':
                    try:
                        if(approval == "Approved"):
                            cat = Application_table.objects.get(pk=request.POST['idbb'])
                            cat.TnP_approval = request.POST['approval']
                            cat.TnP_Comment = request.POST['comment']
                            cat.App_Id = apid
                            cat.Time_Tnp_approval = apr_time.time()
                            cat.date_tnp_approval = apr_time.date()

                            drct = 'nocrest/Static/Images'
                            logo = 'nocrest/Static/Images/mits_logo.png'
                            fname = 'signature.png'
                            current_directory = os.getcwd()
                            print(current_directory)
                            file_path = os.path.join(current_directory,drct, fname)
                            logo_path = os.path.join(current_directory,logo)
                            print("File Path:", file_path)
                            link = f"https://noc.mitsgwalior.in/verifyNOC/?enrollment_number={apid}"  # Replace with your custom link
                            qr = qrcode.QRCode(
                                    version=1,
                                  error_correction=qrcode.constants.ERROR_CORRECT_L,
                                     box_size=10,
                                      border=4,
                                    )
                            qr.add_data(link)
                            qr.make(fit=True)
                            qr_img = qr.make_image(fill_color="black", back_color="white")
                            qr_img_path = f"nocrest/Static/Images/qrcode.png"  # Replace with the path to save the QR code image
                            qrrpath = os.path.join(current_directory,qr_img_path)
                            qr_img_path = qrrpath
                            qr_img.save(qr_img_path)
                            print(qr_img_path)
                            html_template = get_template(os.path.join(current_directory,'nocrest/Static/confnoc.html'))
                            context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                            html_content = html_template.render(context)
                            my_model_data = {'Name': Name,
                                            'designation': designation,
                                            'company': company,
                                            'location': location,
                                            'today_date': today_date,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'stud_branch': stud_branch,
                                            'stud_name': stud_name,
                                            'stud_enr': stud_enr,
                                            'apid':apid,
                                            'file_path':file_path,
                                            'qr_img_path':qr_img_path,
                                            'logo_path':logo_path}

                            subject = 'Testing'
                            message = 'Successfully applied for NO Dues'
                            from_email = 'sdc@mitsgwalior.in'
                            recipient_list = [e_mail]

                            email = EmailMessage(subject, message, from_email, recipient_list)
                            email.content_subtype = "html"
                            email.body = html_content
                            filename = f'{stud_name}_{stud_enr}_{company}_noc.pdf'
                            pdf_file_path = generate_dynamic_pdf(my_model_data, filename)
                            print(pdf_file_path)
                            print(subject)
                            email.attach_file(pdf_file_path)
                            email.send()
                            cat.noc = filename
                            cat.Tnp_approved_by = approved_by
                            cat.save()
                            print("Email send")

                        elif request.POST['approval'] == 'allow':
                                cat = Application_table.objects.get(pk=request.POST['idbb'])
                                cat.Dept_approval = request.POST['approval']
                                cat.Dept_Comment = request.POST['comment']
                                cat.Time_Dept_approval = apr_time.time()
                                cat.date_dept_approval = apr_time.date()
                                cat.D_approved_by = approved_by
                                cat.allow_edit = request.POST['approval']
                                cat.save()
                        else:
                            cat = Application_table.objects.get(pk=request.POST['idbb'])
                            cat.TnP_approval = request.POST['approval']
                            cat.TnP_Comment = request.POST['comment']
                            cat.Time_Tnp_approval = apr_time.time()
                            cat.date_tnp_approval = apr_time.date()
                            cat.Tnp_approved_by = approved_by
                            cat.save()
                            current_directory = os.getcwd()
                            html_template = get_template(os.path.join(current_directory,'nocrest/Static/denynoc.html'))
                            context = {'dept': 'T&P Cell', 'comment':request.POST['comment'] }
                            html_content = html_template.render(context)
                            subject = 'Testing'
                            message = 'Successfully applied for NO Dues'
                            from_email = 'sdc@mitsgwalior.in'
                            recipient_list = [e_mail]
                            email = EmailMessage(subject, message, from_email, recipient_list)
                            email.content_subtype = "html"
                            email.body = html_content
                            email.send()
                    except Exception as e:
                        print("Error agela", e)
            else:
                cat = Application_table.objects.get(pk=request.POST['idbb'])
                if request.POST['approval'] == 'Approved':
                        cat.Dept_approval = request.POST['approval']
                        cat.Dept_Comment = request.POST['comment']
                        cat.Time_Dept_approval = apr_time.time()
                        cat.date_dept_approval = apr_time.date()
                        cat.D_approved_by = approved_by
                        cat.save()
                elif request.POST['approval'] == 'allow':
                        cat.Dept_approval = request.POST['approval']
                        cat.Dept_Comment = request.POST['comment']
                        cat.Time_Dept_approval = apr_time.time()
                        cat.date_dept_approval = apr_time.date()
                        cat.D_approved_by = approved_by
                        cat.allow_edit = request.POST['approval']
                        cat.save()        
                else:
                        cat.Dept_approval = request.POST['approval']
                        cat.Dept_Comment = request.POST['comment']
                        cat.Time_Dept_approval = apr_time.time()
                        cat.date_dept_approval = apr_time.date()
                        cat.D_approved_by = approved_by
                        cat.save()
                        current_directory = os.getcwd()
                        html_template = get_template(os.path.join(current_directory,'nocrest/Static/denynoc.html'))
                        context = {'dept': department, 'comment':request.POST['comment'] }
                        html_content = html_template.render(context)
                        subject = 'Testing'
                        message = 'Successfully applied for NO Dues'
                        from_email = 'sdc@mitsgwalior.in'
                        recipient_list = [e_mail]
                        email = EmailMessage(subject, message, from_email, recipient_list)
                        email.content_subtype = "html"
                        email.body = html_content
                        email.send()


        return redirect('/api/adminDash?clicked=6')
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'success': False, 'error': str(e)})  # Return an error response if needed


@api_view(['GET', 'POST', 'DELETE'])
def BonaEdit(request):
    try:
        if request.method == 'POST':
            print(1111)
            department = request.POST.get('randomdept')
            print("v hjbvuafvb dfjbvb", department)
            print(request.POST.get('idbb'))
            today_date = datetime.now().date()
            Email = request.POST.get('email')
            stud_enr = request.POST.get('enrollmentId')
            stud_name = request.POST.get('studentName')
            father_name = request.POST.get('fathersname')
            semester = request.POST.get('semester')
            session = request.POST.get('session')
            stud_branch = request.POST.get('dept')
            approval = request.POST.get('approval')
            comment = request.POST.get('comment')
            print(approval, comment, stud_enr)
            qry = "select * from nocrest_department where Dep_Id = '{0}'".format(6)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(rec)
            print(rec[0]['Department_name'])
            print(rec[0]['programmme'])
            stud_branch = rec[0]['Department_name']
            qry = "select count(*) from nocrest_bonafidemodel where dept_approval='Approved'"
            cursor = connection.cursor()
            cursor.execute(qry)
            apid = tuple_to_dict.ParseDictSingleRecord(cursor)
            print("gwvdvubwbbf  yfebfebf8og7gw",apid['count(*)'])
            print(stud_branch, Email, stud_enr)
            apr_time = datetime.now()
            print(apr_time)
            date = apr_time.date()
            print(date)
            apid = apid['count(*)'] + 1
            cat = BonafideModel.objects.get(pk=request.POST['idbb'])
            try:
                if request.POST['approval'] == 'Approved':
                        # Update database fields
                        cat.dept_approval = request.POST['approval']
                        cat.dept_comment = request.POST['comment']
                        cat.approval_date = apr_time.date()
                        cat.save()
                        # Render approveBonaf.html template
                        current_directory = os.getcwd()
                        logo = 'nocrest/Static/Images/final_MD_Sign.png'
                        Mitslogo = 'nocrest/Static/Images/mits_logo.png'
                        logo_path = os.path.join(current_directory,logo)
                        Mits_logo_path = os.path.join(current_directory,Mitslogo)
                        approve_bonaf_template_path = os.path.join(current_directory, 'nocrest/Static/approveBonaf.html')
                        approve_bonaf_template = get_template(approve_bonaf_template_path)
                        approve_bonaf_context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                        approve_bonaf_html_content = approve_bonaf_template.render(approve_bonaf_context)

                        # Render BonafidePdf.html template to generate PDF
                        bonafide_pdf_template_path = os.path.join(current_directory, 'nocrest/Static/BonafidePdf.html')
                        bonafide_pdf_template = get_template(bonafide_pdf_template_path)
                        bonafide_pdf_context = {
                            'studname': stud_name,
                            'studenr': stud_enr,
                            'programme': rec[0]['programmme'],
                            'fathername': father_name,
                            'studbranch': stud_branch,
                            'semester': semester,
                            'session': session,
                            'logo_path':logo_path,
                            'mitspath':Mits_logo_path,
                            'apid':apid,
                            'date':date
                        }
                        bonafide_pdf_html_content = bonafide_pdf_template.render(bonafide_pdf_context)

                        # Convert Bonafide PDF HTML content to PDF
                        result = BytesIO()
                        pdf = pisa.pisaDocument(BytesIO(bonafide_pdf_html_content.encode("UTF-8")), result)

                        if not pdf.err:
                            bonafide_pdf_content = result.getvalue()

                            # Save Bonafide PDF to file system
                            pdfs_directory = os.path.join(current_directory, 'pdfs')
                            os.makedirs(pdfs_directory, exist_ok=True)
                            bonafide_pdf_file_name = f"{stud_name}_{stud_enr}_bonafide.pdf"
                            bonafide_pdf_file_path = os.path.join(pdfs_directory, bonafide_pdf_file_name)
                            with open(bonafide_pdf_file_path, 'wb') as pdf_file:
                                pdf_file.write(bonafide_pdf_content)

                            # Attach Bonafide PDF to email
                            email_subject = 'Testing'
                            email_body = 'Successfully applied for NO Dues'
                            from_email = 'suyashu1606.agarwal@gmail.com'
                            recipient_list = [Email]

                            email = EmailMessage(email_subject, email_body, from_email, recipient_list)
                            email.attach_file(bonafide_pdf_file_path)  # Attach Bonafide PDF
                            email.content_subtype = "html"
                            email.body = approve_bonaf_html_content  # Set approveBonaf.html content as email body

                            # Send email
                            email.send()
                            print("Mail Sent")

                        else:
                            print("Failed to generate Bonafide PDF.")
                elif request.POST['approval'] == 'declined':
                        print("Decline horha hai")
                        cat.dept_approval = request.POST['approval']
                        cat.dept_comment = request.POST['comment']
                        cat.approval_date = apr_time.date()
                        cat.save()
                        current_directory = os.getcwd()
                        html_template = get_template(os.path.join(current_directory,'nocrest/Static/denyBonaf.html'))
                        context = {'dept': department, 'comment':request.POST['comment'] }
                        html_content = html_template.render(context)
                        subject = 'Testing'
                        message = 'Bonafide Application Declined!'
                        from_email = 'sdc@mitsgwalior.in'
                        recipient_list = [Email]
                        email = EmailMessage(subject, message, from_email,recipient_list)
                        email.content_subtype = "html"
                        email.body = html_content
                        email.send()
                        print("DENIED BONAF")
            
            except Exception as e:
                    print("Error:", e)
        return redirect('/api/adminDash?clicked=3')
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'success': False, 'error': str(e)})  # Return an error response if needed

@api_view(['GET', 'POST', 'DELETE'])
def Status(request):
      try:
        if request.method == 'POST':
            print('\n\n\n\n')
            print("hWlll")
            role = request.POST.get('Role')
            e_mail = request.POST['Email']
            contact = request.POST['Contact']
            adid = request.POST['id']
            dept = request.POST['dept']
            status = request.POST['status']
            apr_time = datetime.now()
            print(role, e_mail, contact, adid, dept, status, apr_time)
            cat = Admins.objects.get(pk=request.POST.get('id'))
            cat.Role = request.POST.get('Role')
            cat.status = request.POST.get('status')
            cat.save()
            print("saved")
            return redirect('/api/superadmin')
      except Exception as e:
          print("Error", e)



import os
def render_html_to_pdf(template_path, context,folderpath ,filename):
  try:
        template = get_template(template_path)
        html = template.render(context).encode("utf-8")  # Use UTF-8 encoding
        result = BytesIO()
        pdf = pisa.pisaDocument(html, result)  # Pass template_path as filename

        if not pdf.err:
            pdf_content = result.getvalue()

            os.makedirs(folderpath, exist_ok=True)

            # Combine folder path and filename
            if filename:
                with open(filename, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)

            return pdf_content

        return None
  except ValueError as e:
        print("Error: Invalid filename or encoding", e)




def generate_dynamic_pdf(data, filename='output.pdf'):
    try:
        context = {
        'stud_name': data['stud_name'],
        'stud_enr': data['stud_enr'],
        'start_date': data['start_date'],
        'today_date': data['today_date'],
        'end_date': data['end_date'],
        'stud_branch': data['stud_branch'],
        'company': data['company'],
        'designation': data['designation'],
        'Name': data['Name'],
        'location': data['location'],
        'apid':data['apid'],
        'file_path':data['file_path'],
        'qr_img_path':data['qr_img_path'],
        'logo_path':data['logo_path'],
        }
        current_directory = os.getcwd()
        print(current_directory)
        pdf_content = render_html_to_pdf(os.path.join(current_directory,'nocrest/Static/htmltopdf.html'), context, os.path.join(current_directory,'nocrest/Static/'), filename)
        with open(os.path.join(current_directory,'nocrest/Static/', filename), 'wb') as pdf_file:
            pdf_file.write(pdf_content)

        return os.path.join(os.path.join(current_directory,'nocrest/Static/'), filename)

    except Exception as e:
        print("Error generating PDF:", e)
        return None



@api_view(['GET','POST','DELETE'])
def DashAdmin(req):
    contact = req.session.get('contact')
    print(contact)
    q = " select * from nocrest_admins where Contact = '{0}'".format(contact)
    print(q)
    cursor = connection.cursor()
    cursor.execute(q)
    record = tuple_to_dict.ParseDictMultipleRecord(cursor)
    return render(req,"Admindash.html",{'record':record[0]})


@api_view(['GET', 'POST', 'DELETE'])
def verify_noc(request):
    try:
        if request.method == 'GET':
            enrollment_number = request.GET.get('enrollment_number', None)
            if enrollment_number:
                qry = "select * from nocrest_application_table where app_id = '{0}' and tnp_approval = 'Approved'".format(enrollment_number)
                cursor = connection.cursor()
                cursor.execute(qry)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                return render(request, 'Verify.html', {'data': rec})
            else:
                return render(request, 'Verify.html', {'error': 'Enrollment number not provided'})
    except Exception as e:
        # Handle other exceptions appropriately
        return render(request, 'verify_noc.html', {'error': f"Unexpected error: {e}"})


@api_view(['GET','POST','DELETE'])
def VerifyPage(request):
    return render(request, "Verify.html")

@api_view(['GET','POST','DELETE'])
def EditSaveNDDept(req):
    try:
        if req.method == 'GET':
            # print(req.GET['dept'])
            print(1111)
            if req.GET['btn'] == 'edit':
                    print(222)
                    print(req.GET['idbb'])
                    dept = req.GET['randomdept']
                    e_mail = req.GET['Email']
                    if(dept == 'Lib'):
                        cat = NoDues_application_table.objects.get(pk=req.GET['idbb'])
                        cat.EnrollmentId = req.GET['EnrollmentId']
                        cat.Name = req.GET['Name']
                        cat.Lib_approval = req.GET['Dept_approval']
                        cat.Lib_Comment = req.GET['Dept_comment']
                        cat.save()
                        print(444)
                    elif(dept == 'acc'):
                        cat = NoDues_application_table.objects.get(pk=req.GET['idbb'])
                        cat.EnrollmentId = req.GET['EnrollmentId']
                        cat.Name = req.GET['Name']
                        cat.Acc_approval = req.GET['Dept_approval']
                        cat.Acc_Comment = req.GET['Dept_comment']
                        cat.save()
                        current_directory = os.getcwd()
                        html_template = get_template(os.path.join(current_directory,'nocrest/Static/confnodd.html'))
                        context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                        html_content = html_template.render(context)
                        subject = 'Testing'
                        message = 'Successfully applied for NO Dues'
                        from_email = 'sdc@mitsgwalior.in'
                        recipient_list = [e_mail]

                        email = EmailMessage(subject, message, from_email, recipient_list)
                        email.content_subtype = "html"
                        email.body = html_content
                        email.send()
                        print(444)
                    elif(dept == 'Hostel'):
                        cat = NoDues_application_table.objects.get(pk=req.GET['idbb'])
                        cat.EnrollmentId = req.GET['EnrollmentId']
                        cat.Name = req.GET['Name']
                        cat.Hostle_approval = req.GET['Dept_approval']
                        cat.Hostle_Comment= req.GET['Dept_comment']
                        cat.save()
                        print(444)
                    elif(dept == 'tnp'):
                        cat = NoDues_application_table.objects.get(pk=req.GET['idbb'])
                        cat.EnrollmentId = req.GET['EnrollmentId']
                        cat.Name = req.GET['Name']
                        cat.TnP_approval = req.GET['Dept_approval']
                        cat.TnP_Comment= req.GET['Dept_comment']
                        cat.save()
                        print(444)
                    else:
                        print(dept)
                        cat = NoDues_application_table.objects.get(pk=req.GET['idbb'])
                        cat.EnrollmentId = req.GET['EnrollmentId']
                        cat.Name = req.GET['Name']
                        cat.Dept_approval = req.GET['Dept_approval']
                        cat.Dept_Comment= req.GET['Dept_comment']
                        cat.save()
                        print(444)

            else:
                    cat = Application_table.objects.get(pk=req.GET['idbb'])
                    cat.delete()
            return render(req,"Admindash.html")
    except Exception as e:
        print("Error", e)


@api_view(['GET','POST','DELETE'])
def EditSaveTnp(req):
    try:
        if req.method == 'GET':
            print(1111)
            if req.GET['btn'] == 'edit':
                    print(222)
                    print(req.GET['idbb'])
                    cat = Application_table.objects.get(pk=req.GET['idbb'])
                    cat.EnrollmentId = req.GET['EnrollmentId']
                    cat.Name = req.GET['Name']
                    cat.Company = req.GET['Company']
                    cat.Role = req.GET['Role']
                    # cat.App_Id = req.GET['App_Id']
                    cat.Dept_approval = req.GET['Dept_approval']
                    cat.Dept_Comment = req.GET['Dept_comment']
                    cat.TnP_approval = req.GET['TnP_approval']
                    cat.TnP_Comment = req.GET['TnP_Comment']
                    cat.save()
            else:
                    cat = Application_table.objects.get(pk=req.GET['idbb'])
                    cat.delete()
            return render(req,"Tnpdash.html")
    except Exception as e:
        print("Error", e)

@api_view(['GET','POST','DELETE'])
def Approval(req):
    try:
        if req.method =='POST':
            print("TNP ne approve kar doya")
            print(req.POST['id'])
            print(req.POST['dept'])
            print(req.POST['contact'])
    except Exception as e:
        print(e)

@api_view(['GET','POST','DELETE'])
def StudentProfile(req):
    try:
            if req.session['Enrollment'] == '':
                return redirect('/')
            enr = req.session['Enrollment']
            qry = "select * from nocrest_student where EnrollmentId = '{0}'".format(enr)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(rec)
            return render(req, 'Profile.html',{'record':rec})
    except Exception as e:

        print("Error",e)
        
@api_view(['GET', 'POST', 'DELETE'])
def FeedbackForm(req):
    try:
        if req.session['Enrollment'] == '':
            return redirect('/')
        
        id = req.GET.get('id')
        enr = req.session['Enrollment']
        
        qry = "SELECT * FROM nocrest_application_table WHERE EnrollmentId = %s AND id = %s"
        cursor = connection.cursor()
        cursor.execute(qry, (enr, id))
        rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
        print(rec[0]['dept'])
        adid = rec[0]['App_Id']
        Appid = int(adid)
        print(12)
        dept = rec[0]['dept']
        qry = "SELECT * FROM nocrest_department WHERE Dep_Id = %s"
        cursor.execute(qry, (dept,))
        branch = tuple_to_dict.ParseDictMultipleRecord(cursor)
        q = "select * from nocrest_internshipfeedback where noc_approval_id = '{0}'".format(adid)
        cursor = connection.cursor()
        cursor.execute(q)
        record = tuple_to_dict.ParseDictMultipleRecord(cursor)
        if(record):
            return render(req, 'Dashboard.html',{'message':'error'})

        return render(req, 'feedbackform.html', {'record': rec[0], 'branchstud': branch[0]['Department_name'], 'Appid': Appid})
    
    except Exception as e:
        print("Error", e)


@api_view(['GET', 'POST', 'DELETE'])
def ShowFeedback(req):
    try:
            if req.session['Adminemail'] == '':
                print("session khali")
                return redirect('/')
            qry = "select * from nocrest_internshipfeedback"
            cursor = connection.cursor()
            cursor.execute(qry)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            print(len(records))
            return JsonResponse(records,safe=False)
            
    except Exception as e:
        print("Error", e)

from collections import defaultdict
from django.db import connection

def StudentFeedback(req):
    try:
        qry = "SELECT * FROM nocrest_internshipfeedback"
        cursor = connection.cursor()
        cursor.execute(qry)
        records = cursor.fetchall()

        feedback_by_company = defaultdict(list)
        
        for record in records:
            feedback = {
                'company_name': record[4],
                'company_experience_rating': record[5],  
                'work_environment_rating': record[6],  
                'supervisor_rating': record[7], 
                'comment': record[8], 
                'average_experience_rating': 0,
                'average_work_environment_rating': 0,
                'average_supervisor_rating': 0
            }
            feedback_by_company[feedback['company_name']].append(feedback)

        for company_name, feedback_list in feedback_by_company.items():
            total_experience_rating = 0
            total_work_environment_rating = 0
            total_supervisor_rating = 0
            
            for feedback in feedback_list:
                # Check if the ratings are not empty strings
                if feedback['company_experience_rating']:
                    total_experience_rating += int(feedback['company_experience_rating'])
                if feedback['work_environment_rating']:
                    total_work_environment_rating += int(feedback['work_environment_rating'])
                if feedback['supervisor_rating']:
                    total_supervisor_rating += int(feedback['supervisor_rating'])

            if len(feedback_list) > 0:
                # Calculate averages
                feedback_list[0]['average_experience_rating'] = total_experience_rating / len(feedback_list)
                feedback_list[0]['average_work_environment_rating'] = total_work_environment_rating / len(feedback_list)
                feedback_list[0]['average_supervisor_rating'] = total_supervisor_rating / len(feedback_list)

        return render(req, 'Displayfb.html', {'feedback_by_company': dict(feedback_by_company)})

    except Exception as e:
        print("Error", e)


def FeedbackByStudents(req):
    try:
        qry = "SELECT * FROM nocrest_internshipfeedback"
        cursor = connection.cursor()
        cursor.execute(qry)
        records = cursor.fetchall()

        feedback_by_company = defaultdict(list)
        
        for record in records:
            feedback = {
                'company_name': record[4],
                'company_experience_rating': record[5],  
                'work_environment_rating': record[6],  
                'supervisor_rating': record[7], 
                'comment': record[8], 
                'average_experience_rating': 0,
                'average_work_environment_rating': 0,
                'average_supervisor_rating': 0
            }
            feedback_by_company[feedback['company_name']].append(feedback)

        for company_name, feedback_list in feedback_by_company.items():
            total_experience_rating = 0
            total_work_environment_rating = 0
            total_supervisor_rating = 0
            
            for feedback in feedback_list:
                # Check if the ratings are not empty strings
                if feedback['company_experience_rating']:
                    total_experience_rating += int(feedback['company_experience_rating'])
                if feedback['work_environment_rating']:
                    total_work_environment_rating += int(feedback['work_environment_rating'])
                if feedback['supervisor_rating']:
                    total_supervisor_rating += int(feedback['supervisor_rating'])

            if len(feedback_list) > 0:
                # Calculate averages
                feedback_list[0]['average_experience_rating'] = total_experience_rating / len(feedback_list)
                feedback_list[0]['average_work_environment_rating'] = total_work_environment_rating / len(feedback_list)
                feedback_list[0]['average_supervisor_rating'] = total_supervisor_rating / len(feedback_list)
            if req.session['Enrollment'] == '':
                return redirect('/')
            enr = req.session['Enrollment']
            qry = "select * from nocrest_student where EnrollmentId = '{0}'".format(enr)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(rec)
        return render(req, 'Fbdisplay.html', {'feedback_by_company': dict(feedback_by_company),'record':rec})

    except Exception as e:
        print("Error", e)

@api_view(['GET', 'POST', 'DELETE'])
def AllApplications(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            qry = "select * from nocrest_application_table where Dept_approval = '' and Tnp_approval = '' order by App_Date desc"
            cursor = connection.cursor()
            cursor.execute(qry)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            print(len(records))
            return JsonResponse(records,safe=False)
            
    except Exception as e:
        print("Error", e)
@api_view(['GET', 'POST', 'DELETE'])
def AdminApprovedAllApps(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            qry = "select * from nocrest_application_table where (Dept_approval = 'Approved' or TnP_approval='Approved' ) order by App_Date desc"
            cursor = connection.cursor()
            cursor.execute(qry)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            print(len(records))
            return JsonResponse(records,safe=False)
            
    except Exception as e:
        print("Error", e)
@api_view(['GET', 'POST', 'DELETE'])
def AdminDeclinedAllApps(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            qry = "select * from nocrest_application_table where (Dept_approval = 'declined' or TnP_approval='declined' ) order by App_Date desc"
            cursor = connection.cursor()
            cursor.execute(qry)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print("xxxxxxxxxx",records)
            print(len(records))
            return JsonResponse(records,safe=False)
            
    except Exception as e:
        print("Error", e)

@api_view(['GET', 'POST', 'DELETE'])
def BonafApplications(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            dept = req.GET['dept']
            print('DEPARTMENT',dept)
            q = "select * from nocrest_department where department = '{0}'".format(dept)
            cursor = connection.cursor()
            cursor.execute(q)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(rec)
            print(len(rec))
            r = []
            for i in range(len(rec)):
                    m = rec[i]['id']
                    q = "select * from nocrest_bonafidemodel where Branch='{0}' and dept_approval = '' order by application_date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                        print(i)
                        print("sample",result)
                        r += result
            print('RRRRRRRRRRRRR',r)
            print()
            print()
            print()
            print()
           
            return JsonResponse(r,safe=False)
            
    except Exception as e:
        print("Error", e)


@api_view(['GET', 'POST', 'DELETE'])
def ApprovedBonafApplications(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            dept = req.GET['dept']
            print('DEPARTMENT',dept)
            q = "select * from nocrest_department where department = '{0}'".format(dept)
            cursor = connection.cursor()
            cursor.execute(q)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(rec)
            print(len(rec))
            r = []
            for i in range(len(rec)):
                    m = rec[i]['id']
                    q = "select * from nocrest_bonafidemodel where Branch='{0}' and dept_approval = 'Approved' order by application_date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                        print(i)
                        print("sample",result)
                        r += result
            print('RRRRRRRRRRRRR',r)
            print()
            print()
            print()
            print()
           
            return JsonResponse(r,safe=False)
            
    except Exception as e:
        print("Error", e)

@api_view(['GET', 'POST', 'DELETE'])
def DeclinedBonafApplications(req):
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            dept = req.GET['dept']
            print('DEPARTMENT',dept)
            q = "select * from nocrest_department where department = '{0}'".format(dept)
            cursor = connection.cursor()
            cursor.execute(q)
            rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
            print(rec)
            print(len(rec))
            r = []
            for i in range(len(rec)):
                    m = rec[i]['id']
                    q = "select * from nocrest_bonafidemodel where Branch='{0}' and dept_approval = 'declined' order by application_date desc".format(m)
                    cursor = connection.cursor()
                    cursor.execute(q)
                    result = tuple_to_dict.ParseDictMultipleRecord(cursor)
                    if(result):
                        print(i)
                        print("sample",result)
                        r += result
            print('RRRRRRRRRRRRR',r)
            print()
            print()
            print()
            print()
           
            return JsonResponse(r,safe=False)
            
    except Exception as e:
        print("Error", e)

        
@api_view(['GET','POST','DELETE'])
def AdminProfile(req):
    try:
            print("AAGAYA ANDAR")
            
            if req.session['Admincontact'] == '':
                if req.session['Adminemail'] == '':
                    return redirect('/')
            enr = req.session['Adminemail']
            qry = "select * from nocrest_admins where email = '{0}'".format(enr)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(rec)
            if(rec):
                return render(req, 'ADprofile.html',{'record':rec})
            else:
                enr = req.session['Admincontact']
                qry = "select * from nocrest_admins where Contact = '{0}'".format(enr)
                cursor = connection.cursor()
                cursor.execute(qry)
                rec = tuple_to_dict.ParseDictSingleRecord(cursor)
                print(rec)
                return render(req, 'ADprofile.html',{'record':rec})
    except Exception as e:

        print("Error",e)

@api_view(['GET'])
def Companydata(req):
    try:
        qry = "select * from nocrest_application_table where TnP_approval = 'Approved'"
        cursor = connection.cursor()
        cursor.execute(qry)
        rec = tuple_to_dict.ParseDictMultipleRecord(cursor)

        company_counts = {}
        for item in rec:
            company_name = item['Company']
            stipend = int(item.get('stipend', 0))  # Assuming stipend is an integer field
            if company_name in company_counts:
                company_counts[company_name]['total_students'] += 1
                company_counts[company_name]['total_stipend'] += stipend
                company_counts[company_name]['min_stipend'] = min(company_counts[company_name]['min_stipend'], stipend)
                company_counts[company_name]['max_stipend'] = max(company_counts[company_name]['max_stipend'], stipend)
                # Assuming start_date and end_date are available in the item dictionary
                company_counts[company_name]['start_date'] = item.get('startDate', '')
                company_counts[company_name]['end_date'] = item.get('endDate', '')
            else:
                company_counts[company_name] = {
                    'total_students': 1,
                    'total_stipend': stipend,
                    'min_stipend': stipend,
                    'max_stipend': stipend,
                    # Assuming start_date and end_date are available in the item dictionary
                    'start_date': item.get('startDate', ''),
                    'end_date': item.get('endDate', '')
                }

        # Calculate average stipend for companies with multiple entries
        for company_name, data in company_counts.items():
            if data['total_students'] > 1:
                data['average_stipend'] = data['total_stipend'] / data['total_students']
            else:
                data['average_stipend'] = data['total_stipend']

        return render(req, 'Company.html', {'company_counts': company_counts})
    except Exception as e:
        print("Error:", e)
        return HttpResponse(e)

@api_view(['GET', 'POST', 'DELETE'])
def StudentEdit(req):
    try:
        if req.method == 'POST':
            father = req.POST.get('fathers_name')
            address = req.POST.get('Address')
            contact = req.POST.get('contact_Num')
            dept = req.POST.get('Branch')
            password = req.POST.get('password')
            student_id = req.POST.get('idbb')
            student = Student.objects.get(pk=student_id)
            student.fathers_name = father
            student.Address = address
            student.contact_Num = contact
            student.Branch = dept
            student.password = password
            student.save()

            return redirect('/api/studentlogin')
    except Exception as e:
        print("Error:", e)

@api_view(['GET', 'POST', 'DELETE'])
def NOCEditApp(req):
    try:
        if req.method == 'POST':
            enr = req.POST.get('EnrollmentId')
            add = req.POST.get('name')
            nmrcv = req.POST.get('name_reciever')
            dsrcv = req.POST.get('Designation_reciever')
            cnpnm = req.POST.get('companyname')
            strtdt = req.POST.get('startDate')
            enddt = req.POST.get('endDate')
            location = req.POST.get('location')
            drsn = req.POST.get('duration')
            Application_edit = Application_table.objects.get(pk =req.POST.get('idbb') )
            Application_edit.org_address = add
            Application_edit.name_reciever = nmrcv
            Application_edit.Designation_reciever = dsrcv
            Application_edit.Company = cnpnm
            Application_edit.startDate = strtdt
            Application_edit.endDate = enddt
            Application_edit.location = location
            Application_edit.duration = drsn
            Application_edit.Dept_approval = ''
            Application_edit.TnP_approval = ''
            Application_edit.allow_edit = ''
            Application_edit.save()

            return redirect('/api/studentlogin')
    except Exception as e:
        print("Error:", e)

@api_view(['GET', 'POST', 'DELETE'])
def EditDeptAdmin(req):
    try:
        print("aagaya hoon department badalne")
        if req.method == 'POST':
            add = req.POST.get('deptname')
            nmrcv = req.POST.get('department')
            dsrcv = req.POST.get('programme')
            Application_edit = Department.objects.get(pk =req.POST.get('deptid') )
            Application_edit.Department_name = add
            Application_edit.Department = nmrcv
            Application_edit.programmme = dsrcv
            Application_edit.save()

            return redirect('/api/superadmin')
    except Exception as e:
        print("Error:", e)

@api_view(['GET', 'POST', 'DELETE'])
def AddDeptAdmin(req):
    try:
        print("aagaya hoon department badalne")
        if req.method == 'POST':
            qry = 'select count(*) from nocrest_department'
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(rec['count(*)'])
            id= rec['count(*)'] + 1
            add = req.POST.get('deptname')
            nmrcv = req.POST.get('department')
            dsrcv = req.POST.get('programme')
            
            qry = 'SELECT * FROM nocrest_department WHERE Department_name = %s AND Department = %s'
            cursor = connection.cursor()
            cursor.execute(qry, (add, nmrcv))
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            if rec:
                return render(req, "Super.html", {'message': 'error'})
            else:
                data = Department(
                    Dep_Id = id,
                    Department_name = add,
                    Department = nmrcv,
                    programmme = dsrcv
                )
                data.save()
            return redirect('/api/superadmin')
    except Exception as e:
        print("Error:", e)


@api_view(['GET', 'POST', 'DELETE'])
def InternFeedback(req):
    try:
        print("Inside to submit feedback")
        feedback = internfeedback(data=req.POST)
        print(feedback)
        if feedback.is_valid():
            try:
                feedback.save()
                print("Saved")
            except Exception as e:
                print("Error", e)
        return render(req, "feedbackform.html",{'message':'ok'})
    except Exception as e:
        print("Error:", e)


@api_view(['GET', 'POST', 'DELETE'])
def adminEdit(req):
    try:
        if req.method == 'POST':
            email = req.POST.get('Email')
            contact = req.POST.get('Contact')
            dep = req.POST.get('dept')
            passs = req.POST.get('password')
            student_id = req.POST.get('idbb')
            student = Admins.objects.get(pk=student_id)
            student.Email = email
            student.Contact = contact
            student.dept = dep
            student.Password = passs
            student.save()

            return redirect('/api/adminDash')
    except Exception as e:
        print("Error:", e)

@api_view(['GET','POST','DELETE'])
def AdminFaculties(req):
    try:
        if( req.method == 'GET'):


            q = " select * from nocrest_admins"
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)


            if(record):

                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)
@api_view(['GET','POST','DELETE'])
def AdminRoles(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_admins where status ='Active' "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def ShowDepartments(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_department "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)

@api_view(['GET'])
def FDelete(request):
    try:
        if request.method == 'GET':
            # Get the ID from query parameters
            row_id = request.query_params.get('id')
            print(row_id)
            data = Admins.objects.get(pk=request.GET['id'])
            data.delete()
            return redirect('/api/superadmin')
    except Exception as e:
        print("Error", e)

@api_view(['GET','POST','DELETE'])
def AdminStudents(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_student "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)
@api_view(['GET','POST','DELETE'])
def AdminNOCstuds(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_application_table "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)
@api_view(['GET','POST','DELETE'])
def AdminNoDuesstuds(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_nodues_application_table "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")
            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def AdminHostle(req):
    try:
        if( req.method == 'GET'):
            q = " select * from nocrest_nodues_application_table where Hostle_approval = 'approved' "
            print(q)
            cursor = connection.cursor()
            cursor.execute(q)
            record = tuple_to_dict.ParseDictMultipleRecord(cursor)
            if(record):
                print(record)
            else:
                print("No record found")

            return JsonResponse(record, safe=False)
    except Exception as e:
        print("Error",e)

@api_view(['GET','POST','DELETE'])
def SuperAdmin(req):
    try:
        # if req.session['Adminemail'] == '':
        #     return redirect('/')
        ADname = req.session['Adminname']
        qr = "SELECT COUNT(*) FROM nocrest_student"
        cursor = connection.cursor()
        cursor.execute(qr)
        result = cursor.fetchone()  # Fetches the first row of the result

        if result:
            num = result[0]
        else:
            print("No rows returned.")
        qr = "SELECT COUNT(*) FROM nocrest_application_table"
        cursor = connection.cursor()
        cursor.execute(qr)
        result = cursor.fetchone()  # Fetches the first row of the result

        if result:
            nocnum = result[0]
        else:
            print("No rows returned.")
        qr = "SELECT COUNT(*) FROM nocrest_application_table where TnP_approval = 'approved'"
        cursor = connection.cursor()
        cursor.execute(qr)
        result = cursor.fetchone()  # Fetches the first row of the result

        if result:
            noctnp = result[0]
        else:
            print("No rows returned.")
        qr = "SELECT COUNT(*) FROM nocrest_nodues_application_table"
        cursor = connection.cursor()
        cursor.execute(qr)
        result = cursor.fetchone()  # Fetches the first row of the result

        if result:
            nod = result[0]
        else:
            print("No rows returned.")
        qr = "SELECT COUNT(*) FROM nocrest_nodues_application_table where Acc_approval = 'approved'"
        cursor = connection.cursor()
        cursor.execute(qr)
        result = cursor.fetchone()  # Fetches the first row of the result

        if result:
            noduapp = result[0]
        else:
            print("No rows returned.")

        return render(req, "Super.html",{"data":num,"nocdata":nocnum,"noctnp":noctnp,"nod":nod,"nodapp":noduapp,"name":ADname})
    except Exception as e:
        print("Error",e)
        return redirect('/')
@api_view(['GET', 'POST', 'DELETE'])
def AdminApproval(request):
    try:
        if request.method == 'POST':
            tnp_approval = request.POST.get('tnp_approval')
            email = request.POST.get('Email')
            contact = request.POST.get('Contact')
            id = request.POST.get('id')
            dept = request.POST.get('dept')
            dept_approval = request.POST.get('dept_approval')
            clicked = request.POST.get('clicked')

            name = request.POST.get('Name')
            receiver_name = request.POST.get('ReceiverName')
            designation = request.POST.get('Designation')
            company = request.POST.get('Company')
            location = request.POST.get('Location')
            startdate = request.POST.get('startdate')
            endDate = request.POST.get('endDate')
            EnrollmentId = request.POST.get('EnrollmentId')
            App_Id = request.POST.get('App_Id')
            approveby = request.POST.get('adminname')
            AByAdmin = 'admin_'  + approveby 
            # Print the received data
            print("tnp_approval:", tnp_approval)
            print("Email:", email)
            print("Contact:", contact)
            print("ID:", id)
            print("Department:", dept)
            print("dept_approval:", dept_approval)
            print("Clicked:", clicked)
            print("Name:", name)
            print("Receiver Name:", receiver_name)
            print("Designation:", designation)
            print("Company:", company)
            print("Location:", location)
            print("approveby:", approveby)

            if(dept_approval == 'Approved' and tnp_approval == 'Approved') :
                apr_time = datetime.now()
                today_date = apr_time.date()
                qry = "select * from nocrest_department where Dep_Id = '{0}'".format(dept)
                cursor = connection.cursor()
                cursor.execute(qry)
                rec = tuple_to_dict.ParseDictMultipleRecord(cursor)
                print(rec[0]['Department_name'])
                stud_branch = rec[0]['Department_name']
                q="select count(*) from nocrest_application_table where tnp_approval = 'approved'"
                cursor=connection.cursor()
                cursor.execute(q)
                record=tuple_to_dict.ParseDictSingleRecord(cursor)
                apid = record['count(*)'] + 1
                drct = 'nocrest/Static/Images'
                logo = 'nocrest/Static/Images/mits_logo.png'
                fname = 'signature.png'
                current_directory = os.getcwd()
                print(current_directory)
                file_path = os.path.join(current_directory,drct, fname)
                logo_path = os.path.join(current_directory,logo)
                print("File Path:", file_path)
                link = f"https://noc.mitsgwalior.in/verifyNOC/?enrollment_number={apid}"  # Replace with your custom link
                qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
                )
                qr.add_data(link)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img_path = f"nocrest/Static/Images/qrcode.png"  # Replace with the path to save the QR code image
                qrrpath = os.path.join(current_directory,qr_img_path)
                qr_img_path = qrrpath
                qr_img.save(qr_img_path)
                print(qr_img_path)            
                html_template = get_template(os.path.join(current_directory,'nocrest/Static/confnoc.html'))
                context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                html_content = html_template.render(context)
                my_model_data = {'Name': receiver_name,
                                                'designation': designation,
                                                'company': company,
                                                'location': location,
                                                'today_date': today_date,
                                                'start_date': startdate,
                                                'end_date': endDate,
                                                'stud_branch': stud_branch,
                                                'stud_name': name,
                                                'stud_enr': EnrollmentId,
                                                'apid':apid,
                                                'file_path':file_path,
                                                'qr_img_path':qr_img_path,
                                                'logo_path':logo_path}

                subject = 'Testing'
                message = 'Successfully applied for NO Dues'
                from_email = 'sdc@mitsgwalior.in'
                recipient_list = [email]
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.content_subtype = "html"
                email.body = html_content
                filename = f'{name}_{EnrollmentId}_{company}_noc.pdf'
                pdf_file_path = generate_dynamic_pdf(my_model_data, filename)
                print(pdf_file_path)
                print(subject)
                email.attach_file(pdf_file_path)
                email.send()
                cat = Application_table.objects.get(pk=request.POST['id'])
                cat.Dept_approval = dept_approval
                cat.TnP_approval = tnp_approval
                cat.D_approved_by = AByAdmin
                cat.Tnp_approved_by = AByAdmin
                cat.save()
                print("Saved")
            return redirect('/api/superadmin')

            # Now you can use the extracted data as needed
            # Example:
            # Save the data to the database, perform operations, etc.

            return JsonResponse({'message': 'Data received successfully'}, status=200)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'error': 'An error occurred'}, status=500)
