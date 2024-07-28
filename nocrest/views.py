from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.decorators import api_view, parser_classes
import tempfile
from .models import Admins 
from django.db.models import Q
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
from django.contrib.auth.hashers import make_password, check_password
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
  if not req.user.is_authenticated:
        return redirect('/')
  try:
    username = req.user.username
    email = req.user.email
    first_name = req.user.first_name
    last_name = req.user.last_name
    em = email[-13:]
    print(first_name)
    print(email)
    print(username)
    if(em == 'mitsgl.ac.in'):
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
        # print(record[0]['Role'])
        if(record):
            req.session['Admincontact'] = record[0]['Contact']
            req.session['Adminname'] = record[0]['name']
            req.session['RoleAdmin'] = record[0]['Role']
            req.session['Ad_Status'] = record[0]['status']
            if(record[0]['Role']=='admin'):
                return redirect ('/api/superadmin')
            else:
                return redirect ('/api/adminDash')
        else:
            return render(req, "ADSignup.html")
    # else:
    #     return redirect('/')
  except Exception as e:
      print(e)
      return redirect('/')


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def login(request):
    return render(request, 'Frontpage.html')
def custom_logout(request):
  try:
    logout(request)
    # Redirect to the front page or any other desired page
    return redirect('/')  # Replace 'frontpage' with the actual name or URL of your front page
  except Exception as e:
      print(e)

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        if not uploaded_file.name.endswith('.xlsx'):
            return JsonResponse({'status': 'Invalid file format. Please upload an Excel file.'}, status=400)
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            return JsonResponse({'status': f'Error reading Excel file: {str(e)}'}, status=400)
        data_dict = df.to_dict(orient='records')
        added_count = 0
        skipped_count = 0
        for record in data_dict:
            enrollment_id = record.get('EnrollmentId')
            if not enrollment_id:
                continue
            if Graduated.objects.filter(EnrollmentId=enrollment_id).exists():
                skipped_count += 1
                continue

            try:
                Graduated.objects.create(**record)
                added_count += 1
            except Exception as e:
                return JsonResponse({'status': f'Error saving record to database: {str(e)}'}, status=400)

        return JsonResponse({'status': f'File uploaded successfully. {added_count} records added, {skipped_count} records skipped.'})
    else:
        return JsonResponse({'status': 'Invalid request'}, status=400)


@api_view(['GET','POST','DELETE'])
def Adsignup(req):
    return render(req, 'ADsignup.html')

@api_view(['GET','POST'])
def Frontpage(req):
    try:
        
        req.session['Admincontact'] = ''
        req.session['AdminPass'] = ''
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

from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
def StudentLogin(request):
    if request.method == 'POST':
        username = request.POST.get('EnrollmentId')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Missing username or password'}, status=400)
        
        try:
            student = Student.objects.get(EnrollmentId=username)
            
            if check_password(password,student.password):
                # Instead of using Django's login, just set session variables
                request.session['Enrollment'] = username
                request.session['is_authenticated'] = True
                request.session['StudPass'] = password
                return get_dashboard_data(request, username)
            else:
                return render(request, "Frontpage.html", {"msg": 'Incorrect Password'})
        except Student.DoesNotExist:
            return render(request, "Frontpage.html", {"msg": 'Kindly Signup First'})
    
    username = request.session.get('Enrollment')
    return get_dashboard_data(request, username) if username else redirect('/')

def get_dashboard_data(request, username):
    try:
        student = Student.objects.get(EnrollmentId=username)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM nocrest_graduated WHERE enrollmentid = %s", [username])
            is_graduated = cursor.fetchone() is not None
            
            cursor.execute("SELECT * FROM nocrest_exitsurvey WHERE enrollmentid = %s", [username])
            has_exit_survey = cursor.fetchone() is not None
            
            cursor.execute("SELECT * FROM nocrest_nodues_application_table WHERE EnrollmentId = %s", [username])
            has_no_dues = cursor.fetchone() is not None
            
            cursor.execute("SELECT Department_name FROM nocrest_department WHERE Dep_Id = %s", [student.Branch])
            department = cursor.fetchone()
            department = department[0] if department else None
            
            cursor.execute("SELECT * FROM nocrest_application_table WHERE EnrollmentId = %s", [username])
            has_applied_noc = cursor.fetchone() is not None

        check = 2 if has_exit_survey else (1 if is_graduated else 0)
        btndisp = 1 if has_no_dues else (0 if has_exit_survey else 1000)

        context = {
            'record': student.__dict__,
            'check': check,
            'branchstud': department,
            'btndisp': btndisp,
            'has_applied_noc': has_applied_noc
        }

        return render(request, "Dashboard.html", context)
    except Student.DoesNotExist:
        return redirect('/')
    except Exception as e:
        print(f"Error in get_dashboard_data: {str(e)}")
        return redirect('/')
    
try:
    @csrf_exempt
    @api_view(['GET', 'POST', 'DELETE'])
    def StudentREg(req):
        print("I'm in StudentREg")
        if req.method == 'GET':
            try:
                username = req.GET.get('EnrollmentId')
                password = req.GET.get('password')
                req.session['StudPass'] = password
                req.session['Enrollment'] = username
                
                # Encrypt the password
                PassW = make_password(password)
                
                # Create a copy of GET data and update the password
                data = req.GET.copy()
                data['password'] = PassW
                
                # Use the modified data for serialization
                contact = contactserialiser(data=data)
                print("Serializer:", contact)
                
                if contact.is_valid():
                    print("Data is valid")
                    try:
                        contact.save()
                        print("Save successful")
                        print(f"Username: {username}, Password: [ENCRYPTED]")
                        return redirect("/api/studentlogin")
                    except Exception as e:
                        print(f"Error during save: {e}")
                        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    print("Serializer errors:", contact.errors)
                    return Response(contact.errors, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                print("Error in StudentREg:", str(e))
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
except Exception as e:
    print(e)
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


from rest_framework.parsers import MultiPartParser, FormParser

@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])
def AdminREg(req):
    try:
        if req.method == 'GET':
            role = req.GET.get('Role')
            name = req.GET.get('name')
            email = req.GET.get('Email')
            dept = req.GET.get('dept')
            contact = req.GET.get('Contact')
            password = req.GET.get('Password')
            stat = req.GET.get('status')
            PassW = make_password(password)
            print(role, name, email, dept, contact, password, stat)
            admin_data = {
                'role': role,
                'name': name,
                'email': email,
                'dept': dept,
                'contact': contact,
                'password': PassW,
                'status': stat
            }
            admin_serializer = Batchserialiser(data=admin_data)
            if admin_serializer.is_valid():
                admin_serializer.save()
                print("Saved")
            else:
                return redirect('/')
            req.session['Admincontact'] = contact
            req.session['AdminPass'] = password
            return redirect("/api/adminDash")
        
        elif req.method == 'POST':
            role = req.POST.get('Role')
            name = req.POST.get('name')
            email = req.POST.get('Email')
            dept = req.POST.get('dept')
            contact = req.POST.get('Contact')
            password = req.POST.get('Password')
            stat = req.POST.get('status')
            signature = req.FILES.get('signature')
            PassW = make_password(password)
            # Ensure the directory exists
            image_dir = "nocrest\Static\Images"
            os.makedirs(image_dir, exist_ok=True)

            # Create the file path
            signature_filename = f"{name}_{dept}.png"
            signature_filepath = os.path.join(image_dir, signature_filename)

            with open(signature_filepath, 'wb+') as destination:
                for chunk in signature.chunks():
                    destination.write(chunk)

            print(role, name, email, dept, contact, password, stat, signature_filepath)
            
            admin_data = {
                'Role': role,
                'name': name,
                'Email': email,
                'dept': dept,
                'Contact': contact,
                'Password': PassW,
                'status': stat,
                'signature': signature_filename  # Save the file name to the database
            }

            admin_serializer = Batchserialiser(data=admin_data)
            if admin_serializer.is_valid():
                admin_serializer.save()
                print("Saved")
                req.session['Admincontact'] = contact
                req.session['AdminPass'] = password
            else:
                return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return redirect("/api/adminDash")

    except Exception as e:
        print("Error", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET','POST','DELETE'])
def Deptfp(req):
    try:
        req.session['Admincontact'] = ''
        req.session['AdminPass'] = ''
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
    # if(req.session['RoleAdmin'] == 'admin'):
    #     return redirect('/api/superadmin')
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
def DeptLogin(request):
    if request.method == 'POST':
        contact = request.POST.get('Contact')
        password = request.POST.get('password')
       
        if not contact or not password:
            return JsonResponse({'error': 'Missing contact or password'}, status=400)
       
        try:
            admin = Admins.objects.get(Q(Contact=contact) | Q(Email=contact))
            print(check_password(password, admin.Password))
            if check_password(password, admin.Password):
                request.session['Admincontact'] = admin.Contact
                request.session['Adminemail'] = admin.Email
                request.session['RoleAdmin'] = admin.Role
                request.session['Ad_Status'] = admin.status
                request.session['AdminPass'] = password
                return redirect('/api/adminDash')
            else:
                return render(request, "Adminfp.html", {"msg": 'Incorrect Password'})
        except Admins.DoesNotExist:
            return render(request, "Adminfp.html", {"msg": 'Kindly Signup First'})
   
#     admin_contact = request.session.get('Admincontact')
#     if admin_contact:
#         admin = Admins.objects.get(Contact=admin_contact)
#         return get_admin_dashboard_data(request, admin)
#     return redirect('/')

# def get_admin_dashboard_data(request, admin):
#     try:
#         context = {}
        
#         if admin.dept == 'Tnp':
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table WHERE dept_approval = 'approved' AND tnp_approval = ''")
#                 context['pending_tnp_approvals'] = cursor.fetchone()[0]
                
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table WHERE tnp_approval = 'approved'")
#                 context['tnp_approved'] = cursor.fetchone()[0]
                
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table")
#                 context['total_applications'] = cursor.fetchone()[0]
                
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table WHERE dept_approval = 'Approved' AND Tnp_approval = 'Approved'")
#                 context['fully_approved'] = cursor.fetchone()[0]
#         else:
#             departments = Admins.objects.filter(dept=admin.dept).values_list('id', flat=True)
            
#             with connection.cursor() as cursor:
#                 pending_applications = []
#                 approved_applications = []
#                 fully_approved_applications = []
                
#                 for dept_id in departments:
#                     cursor.execute("SELECT * FROM nocrest_application_table WHERE dept=%s AND dept_approval = '' ORDER BY App_Date DESC", [dept_id])
#                     pending_applications.extend(cursor.fetchall())
                    
#                     cursor.execute("SELECT * FROM nocrest_application_table WHERE dept=%s AND dept_approval = 'approved' ORDER BY App_Date DESC", [dept_id])
#                     approved_applications.extend(cursor.fetchall())
                    
#                     cursor.execute("SELECT * FROM nocrest_application_table WHERE dept_approval = 'Approved' AND Tnp_approval = 'Approved' AND dept=%s", [dept_id])
#                     fully_approved_applications.extend(cursor.fetchall())
                
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table")
#                 context['total_applications'] = cursor.fetchone()[0]
                
#                 cursor.execute("SELECT COUNT(*) FROM nocrest_application_table WHERE dept_approval = 'Approved' AND Tnp_approval = 'Approved'")
#                 context['fully_approved'] = cursor.fetchone()[0]
            
#             context['pending_applications'] = pending_applications
#             context['approved_applications'] = approved_applications
#             context['fully_approved_applications'] = fully_approved_applications

#         return render(request, "adminDash.html", context)
#     except Exception as e:
#         print(f"Error in get_admin_dashboard_data: {str(e)}")
#         return redirect('/')


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
            title = req.POST.get('title')
            Name_reciever = title + " "+Name_reciever
            if 'offerletter' in req.FILES:
                offerLetter_file = req.FILES['offerletter']
    # Continue with your code to save or process the file
            else:
    # Handle the case where the file is not uploaded
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

            # contactdata.save()
            try:
             current_directory = os.getcwd()
             html_template = get_template(os.path.join(current_directory,'nocrest/Static/emailnoc.html'))
            except Exception as error:
                return HttpResponse(error)
            # try:
            #     context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
            #     html_content = html_template.render(context)
            #     subject = 'Testing'
            #     message = 'Successfully applied for NO Dues'
            #     from_email = 'suyashu1606.agarwal@gmail.com'
            #     recipient_list = [email]

            #     email = EmailMessage(subject, message, from_email, recipient_list)
            #     email.content_subtype = "html"
            #     email.body = html_content

            # # Attempt to send email

            #     email.send()
            #     print("Mail Sent")
            # except Exception as email_exception:
            #     print("Email sending failed:", email_exception)
            #     return HttpResponse(email_exception)
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
            html_template = get_template(os.path.join(current_directory,'nocrest/Static/AppliedBonaf.html'))
            context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
            html_content = html_template.render(context)
            subject = 'Testing'
            message = 'Successfully applied for Bonafide'
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
                email = req.POST.get('email')
                dept = req.POST.get('department')
                poy = req.POST.get('passOutYear')
                fname = req.POST.get('fathersname')
                brn = req.POST.get('branch')
                add = req.POST.get('address')
                mob = req.POST.get('mobile')
                hstl = req.POST.get('hostel')
                fdue = req.POST.get('fees_due')
                preport = req.POST.get('project_report')
                cmoney = req.POST.get('caution_money')
                accname = req.POST.get('account_holder_name')
                bankname = req.POST.get('bank_name')
                accnum = req.POST.get('account_number')
                ifsc = req.POST.get('ifsc_code')
                qry = "select Department from nocrest_department where Dep_Id = '{0}'".format(dept)
                cursor = connection.cursor()
                cursor.execute(qry)
                records = tuple_to_dict.ParseDictSingleRecord(cursor)
                print("xxxxxxxxxx",records)
                print(len(records))
                print(records['Department'])
                dept = records['Department']
                apply = 1
                current_datetime = datetime.now()
                current_date = current_datetime.date()
                current_time = current_datetime.time()
                print(current_date, current_time,email)
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
                    App_time=time,
                    passOutYear = poy,
                    hostel = hstl,
                    fees_due = fdue,
                    project_report = preport,
                    caution_money = cmoney,
                    account_number = accnum,
                    account_holder_name = accname,
                    bank_name = bankname,
                    ifsc_code = ifsc,

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

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
def handle_uploaded_file(file, enrollment_id, name,file_type):
    _, extension = os.path.splitext(file.name)
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{enrollment_id}_{name}_{file_type}_{extension}"
    path = default_storage.save(f'offer_letters/{new_filename}', ContentFile(file.read()))
    return os.path.join(settings.MEDIA_ROOT, path)

@api_view(['GET', 'POST'])
def ExitSurveySubmit(req):
    try:
        if req.method == 'POST':
            enr = req.POST.get('EnrollmentId')
            print(f"Enrollment ID: {enr}")
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
                phone = req.POST.get('mobile')
                apply = req.POST.get('apply')
                dob = req.POST.get('dob')
                gender = req.POST.get('gender')
                course = req.POST.get('course')
                branch = req.POST.get('branch')
                rate_faculty = req.POST.get('rate_faculty')
                teaching_methods = req.POST.get('teaching_methods')
                syllabus_completion = req.POST.get('syllabus_completion')
                course_relevance = req.POST.get('course_relevance')
                teacher_preparedness = req.POST.get('teacher_preparedness')
                course_outcomes = req.POST.get('course_outcomes')
                soft_skills = req.POST.get('soft_skills')
                internships_support = req.POST.get('internships_support')
                student_orgs = req.POST.get('student_orgs')
                curricular_extracurricular = req.POST.get('curricular_extracurricular')
                quizzes = req.POST.get('quizzes')
                evaluation_fairness = req.POST.get('fairness')
                library_resources = req.POST.get('library_resources')
                curriculum_flexibility = req.POST.get('curriculum')
                nptel_moocs = req.POST.get('npt')
                full_semester_internship = req.POST.get('internship')
                training_placement = req.POST.get('placement')
                internship_company = req.POST.get('internship_company')
                internship_certificate = req.POST.get('internship_certificate')
                job_selection = req.POST.get('job_selection')
                outside_job_offer = req.POST.get('outside_job_offers')
                outside_job_letter = req.FILES.get('outside_job_offer_letter')
                file_fields = [
                'offer_letter_1', 'offer_letter_2', 'offer_letter_3', 'offer_letter_4', 'offer_letter_5',
                'outside_job_offer_letter', 'gate_scorecard', 'entrance_exam_scorecards',
                'higher_education_documents', 'final_semester_document','stipend_proof_document'
                ]

                file_paths = {}

                for field in file_fields:
                    if field in req.FILES:
                        file = req.FILES[field]
                        file_path = handle_uploaded_file(file, enrollmentid, name,field)
                        file_paths[field] = file_path
                        print(f"{field} saved at: {file_path}")
                    else:
                        file_paths[field] = None
                    
                
                
                
                # offeletter_1 = req.FILES.get('offer_letter_1')
                # offeletter_2 = req.FILES.get('offer_letter_2')
                # offeletter_3 = req.FILES.get('offer_letter_3')
                # offeletter_4 = req.FILES.get('offer_letter_4')
                # offeletter_5 = req.FILES.get('offer_letter_5')
                multiple_offer_companies = req.POST.get('oncampus_job_offers')
                multiple_offer_letters = req.FILES.get('oncampus_job_offer_letter')
                opted_job_or_pg = req.POST.get('post_graduation')
                further_study_details = req.POST.get('further_study_details')
                joining_company = req.POST.get('joining_company')
                qualified_gate = req.POST.get('gate_qualified')
                gate_rank = req.POST.get('gate_rank')
                gate_scorecard = req.FILES.get('gate_scorecard')
                appeared_for_exams = req.POST.get('exams_appeared[]')
                other_exam_name = req.POST.get('other_exam_name')
                score_cards_all = req.FILES.get('entrance_exam_scorecards')
                percentile = req.POST.get('exam_scores')
                mtech_university = req.POST.get('mtech_university')
                mba_college = req.POST.get('mba_college')
                admission_letter = req.FILES.get('higher_education_documents')
                any_other_competitive_exams = req.POST.get('other_exams_text')
                donate_caution_money = req.POST.get('caution_money_donation')
                final_semester_choice = req.POST.get('final_semester_choice')
                final_year_internship = req.POST.get('final_project_organization')
                final_internship_stipend = req.POST.get('final_internship_stipend')
                final_internship_stipend_amount = req.POST.get('final_internship_stipend_amount')
                internship_company_process = req.POST.get('internship_company_process')
                job_offer_extension = req.POST.get('job_offer_extension')
                final_semester_internship_doc = req.FILES.get('final_semester_document')
                permanent_email = req.POST.get('permanent_Email')
                contact_num = req.POST.get('Contact_Num')
                parent_contact_num = req.POST.get('parent_Contact_Num')
                home_town = req.POST.get('home_town')
                permanent_address = req.POST.get('permanent_address')
                suggestions = req.POST.get('suggestions')
                current_datetime = datetime.now()
                current_date_str = current_datetime.date()
                current_time_str = current_datetime.time()

                # Print file names for debugging
                # print(f"Outside job letter: {outside_job_letter.name if outside_job_letter else 'None'}")
                # print(f"Offer letter 1: {offeletter_1.name if offeletter_1 else 'None'}")
                # print(f"Offer letter 2: {offeletter_2.name if offeletter_2 else 'None'}")
                # print(f"Offer letter 3: {offeletter_3.name if offeletter_3 else 'None'}")
                # print(f"Offer letter 4: {offeletter_4.name if offeletter_4 else 'None'}")
                # print(f"Offer letter 5: {offeletter_5.name if offeletter_5 else 'None'}")
                # print(f"Multiple offer letters: {multiple_offer_letters.name if multiple_offer_letters else 'None'}")
                # print(f"Gate scorecard: {gate_scorecard.name if gate_scorecard else 'None'}")
                # print(f"Score cards all: {score_cards_all.name if score_cards_all else 'None'}")
                # print(f"Admission letter: {admission_letter.name if admission_letter else 'None'}")
                # print(f"Final semester internship doc: {final_semester_internship_doc.name if final_semester_internship_doc else 'None'}")

                # Create the ExitSurvey instance
                survey_data = ExitSurvey(
                    Name=name,
                    EnrollmentId=enrollmentid,
                    Email=email,
                    Phone=phone,
                    Apply=apply,
                    DOB=dob,
                    Gender=gender,
                    Course=course,
                    Branch=branch,
                    RateFaculty=rate_faculty,
                    TeachingMethods=teaching_methods,
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
                    InternshipCompany=internship_company,
                    InternshipCertificate=internship_certificate,
                    JobSelection=job_selection,
                    OutsideJobOffer=outside_job_offer,
                    offer_letter_1=file_paths['offer_letter_1'],
                    offer_letter_2=file_paths['offer_letter_2'],
                    offer_letter_3=file_paths['offer_letter_3'],
                    offer_letter_4=file_paths['offer_letter_4'],
                    offer_letter_5=file_paths['offer_letter_5'],
                    OutsideJobLetter=file_paths['outside_job_offer_letter'],
                    GateScorecard=file_paths['gate_scorecard'],
                    ScoreCardsAll=file_paths['entrance_exam_scorecards'],
                    AdmissionLetter=file_paths['higher_education_documents'],
                    FinalSemesterInternshipDoc=file_paths['final_semester_document'],
                    StipendDocProof=file_paths['stipend_proof_document'],
                    MultipleOfferCompanies=multiple_offer_companies,
                    OptedJoborPG=opted_job_or_pg,
                    FurtherStudyDetails=further_study_details,
                    JoiningCompany=joining_company,
                    QualifiedGate=qualified_gate,
                    GateRank=gate_rank,
                    AppearedForExams=appeared_for_exams,
                    OtherExamName=other_exam_name,
                    Percentile=percentile,
                    MTechUniversity=mtech_university,
                    MBACollege=mba_college,
                    AnyOtherCompetitiveExams=any_other_competitive_exams,
                    DonateCautionMoney=donate_caution_money,
                    FinalSemesterChoice=final_semester_choice,
                    FinalYearInternship=final_year_internship,
                    FinalInternshipStipend=final_internship_stipend,
                    FinalInternshipStipendAmount=final_internship_stipend_amount,
                    InternshipCompanyProcess=internship_company_process,
                    JobOfferExtension=job_offer_extension,
                    PermanentEmail=permanent_email,
                    ContactNum=contact_num,
                    ParentContactNum=parent_contact_num,
                    HomeTown=home_town,
                    PermanentAddress=permanent_address,
                    Suggestions=suggestions,
                    AppDate=current_date_str,
                    AppTime=current_time_str,
                )

                # Handle file fields separately
                # if outside_job_letter:
                #     survey_data.OutsideJobLetter = outside_job_letter.name
                # if offeletter_1:
                #     survey_data.offer_letter_1 = offeletter_1.name
                # if offeletter_2:
                #     survey_data.offer_letter_2 = offeletter_2.name
                # if offeletter_3:
                #     survey_data.offer_letter_3 = offeletter_3.name
                # if offeletter_4:
                #     survey_data.offer_letter_4 = offeletter_4.name
                # if offeletter_5:
                #     survey_data.offer_letter_5 = offeletter_5.name
                # if multiple_offer_letters:
                #     survey_data.MultipleOfferLetters = multiple_offer_letters.name
                # if gate_scorecard:
                #     survey_data.GateScorecard = gate_scorecard.name
                # if score_cards_all:
                #     survey_data.ScoreCardsAll = score_cards_all.name
                # if admission_letter:
                #     survey_data.AdmissionLetter = admission_letter.name
                # if final_semester_internship_doc:
                #     survey_data.FinalSemesterInternshipDoc = final_semester_internship_doc.name

                # Save the survey data
                survey_data.save()

                print("Survey data saved successfully")

                # Verify saved data
                saved_survey = ExitSurvey.objects.get(id=survey_data.id)
                print(f"Saved OutsideJobLetter: {saved_survey.OutsideJobLetter}")
                print(f"Saved offer_letter_1: {saved_survey.offer_letter_1}")
                print(f"Saved offer_letter_2: {saved_survey.offer_letter_2}")
                print(f"Saved offer_letter_3: {saved_survey.offer_letter_3}")
                print(f"Saved offer_letter_4: {saved_survey.offer_letter_4}")
                print(f"Saved offer_letter_5: {saved_survey.offer_letter_5}")
                print(f"Saved MultipleOfferLetters: {saved_survey.MultipleOfferLetters}")
                print(f"Saved GateScorecard: {saved_survey.GateScorecard}")
                # print(f"Saved ScoreCardsAll: {saved_survey.ScoreCardsAll}")
                # print(f"Saved AdmissionLetter: {saved_survey.AdmissionLetter}")
                # print(f"Saved FinalSemesterInternshipDoc: {saved_survey.FinalSemesterInternshipDoc}")

                # Prepare and send the email
                current_directory = os.getcwd()
                html_template = get_template(os.path.join(current_directory, 'nocrest/Static/emailnodues.html'))
                context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                html_content = html_template.render(context)
                subject = 'Exit Survey Submission Confirmation'
                message = 'Thank you for submitting the exit survey. Your responses have been recorded successfully.'
                from_email = 'your_email@gmail.com'  # Sender's email address
                recipient_list = [email]  # List of recipient email addresses
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.content_subtype = "html"  # Set the content type to HTML
                email.body = html_content
                # email.send()
                return render(req, "Dashboard.html", {'message': 'ok'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return render(req, "Frontpage.html")
    

@api_view(['GET','POST'])
def AboutDev(req):
    try:
        return render(req, "about.html")
    except Exception as e:
        print("Error",e)


@api_view(['GET','POST','DELETE'])
def ShowAppliedstudent(req):
    try:
         if req.session['Adminemail'] == '':
             print("session khali")
             return redirect('/')
         if(req.session['Ad_Status'] == 'passive'):
                return redirect('/')
         elif req.method == 'GET':
            department = req.GET.get('dept')
            print(req.GET.get('dept'))
            rec = []
            print(department)
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
            query = " select * from nocrest_department where Department = {0}".format(department)
            if(department == 'Tnp'):
                department = 'TnP_approval'
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(department)
            elif(department == 'Hostel'):
                department='Hostle_approval'
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(department)
            elif(department == 'Lib'):
                de = 'Lib_approval'
                q = "select * from nocrest_NoDues_application_table where {0} = ''  order by App_Date desc".format(de)
            elif( department == 'acc'):
                department+="Acc_approval"
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
def NoDuesAccAppliedstudent(req):
    try:
         if req.method == 'GET':

            q = "SELECT * FROM nocrest_NoDues_application_table WHERE (dept_approval = 'approved' AND Tnp_approval = 'approved' AND hostle_approval = 'approved' AND lib_approval = 'approved' AND Acc_approval = '')  order by App_Date desc"
            cursor = connection.cursor()
            cursor.execute(q)
            records = tuple_to_dict.ParseDictMultipleRecord(cursor)
            dues_amount = []
            print("xxxxxxxxxx",records)
            if(records):
                for i in range(len(records)):
                    amt = 0
                    for key in ['TnP_amount', 'Lib_amount', 'Hostle_amount', 'Genoffice_amount', 'Dept_amount', 'Exam_amount']:
                        value = records[i][key]
                        amt += int(value) if value != '' else 0
                    dues_amount.append(amt)
                    print(dues_amount)
                    response_data = {
                    'records': records,
                    'dues_amount': dues_amount
                }
                
                return JsonResponse(response_data, safe=False)
                # return JsonResponse(records,dues_amount,safe=False)
            else:
                return render(req,"Adminfp.html")
    except Exception as e:
        print("Error", e)


@api_view(['GET','POST','DELETE'])
def AppliedStudeApproved(req):
    try:
         if req.session['Adminemail'] == '':
             return redirect('/')
         if(req.session['Ad_Status'] == 'passive'):
                return
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
         if(req.session['Ad_Status'] == 'passive'):
                return
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
    if(req.session['Ad_Status'] == 'passive'):
                return
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
    if(req.session['Ad_Status'] == 'passive'):
                return
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
            # print(rec[0]['programmme'])
            stud_branch = rec[0]['Department_name']
            qtry = "select image from nocrest_student where EnrollmentId = '{0}'".format(stud_enr)
            cursor = connection.cursor()
            cursor.execute(qtry)
            image = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(image['image'])
            qry = "select count(*) from nocrest_bonafidemodel where dept_approval='Approved'"
            cursor = connection.cursor()
            cursor.execute(qry)
            apid = tuple_to_dict.ParseDictSingleRecord(cursor)
            print("gwvdvubwbbf  yfebfebf8og7gw",apid['count(*)'])
            query = 'select * from nocrest_admins where Contact = {0}'.format(request.session['Admincontact'])
            cursor = connection.cursor()
            cursor.execute(query)
            sign = tuple_to_dict.ParseDictSingleRecord(cursor)
            tough = sign['signature']
            print(sign)
            print(stud_branch, Email, stud_enr,tough)
            print("ibubibgubgrbgbgibeunb")
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
                        # cat.save()
                        # Render approveBonaf.html template
                        current_directory = os.getcwd()
                        logo = f'nocrest/Static/Images/{tough}'
                        Mitslogo = 'nocrest/Static/Images/mits_logo.png'
                        logo_path = os.path.join(current_directory,logo)
                        relative_path = "pdfs/"
                        image_path = os.path.normpath(os.path.join(current_directory, relative_path,image['image'])).replace('\\', '/').lstrip('/')                        
                        Mits_logo_path = os.path.join(current_directory,Mitslogo)
                        approve_bonaf_template_path = os.path.join(current_directory, 'nocrest/Static/approveBonaf.html')
                        approve_bonaf_template = get_template(approve_bonaf_template_path)
                        approve_bonaf_context = {'variable1': 'Value 1', 'variable2': 'Value 2'}
                        approve_bonaf_html_content = approve_bonaf_template.render(approve_bonaf_context)
                        print("image_path",image_path)
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
                            'date':date,
                            'image':image_path
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
        if req.method == 'POST':
            # print(req.GET['dept'])
                    print(1111)
            # if req.POST['btn'] == 'edit':
                    print(222)
                    print(req.POST.get('idbb'))
                    dept = req.POST.get('randomdept')
                    e_mail = req.POST.get('Email')
                    amount = req.POST['Dept_amount']
                    print("Due hai ", amount,"ka")
                    if(dept == 'Lib'):
                        cat = NoDues_application_table.objects.get(pk=req.POST['idbb'])
                        cat.EnrollmentId = req.POST['EnrollmentId']
                        cat.Name = req.POST['Name']
                        cat.Lib_approval = req.POST['Dept_approval']
                        cat.Lib_Comment = req.POST['Dept_comment']
                        cat.save()
                        print(444)
                    elif(dept == 'acc'):
                        cat = NoDues_application_table.objects.get(pk=req.POST['idbb'])
                        cat.EnrollmentId = req.POST['EnrollmentId']
                        cat.Name = req.POST['Name']
                        cat.Acc_approval = req.POST['Dept_approval']
                        cat.Acc_Comment = req.POST['Dept_comment']
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
                        cat = NoDues_application_table.objects.get(pk=req.POST['idbb'])
                        cat.EnrollmentId = req.POST['EnrollmentId']
                        cat.Name = req.POST['Name']
                        cat.Hostle_approval = req.POST['Dept_approval']
                        cat.Hostle_Comment= req.POST['Dept_comment']
                        cat.save()
                        print(444)
                    elif(dept == 'Tnp'):
                        cat = NoDues_application_table.objects.get(pk=req.POST['idbb'])
                        # cat.EnrollmentId = req.POST['EnrollmentId']
                        # cat.Name = req.POST['Name']
                        cat.TnP_approval = req.POST['Dept_approval']
                        cat.TnP_Comment= req.POST['Dept_comment']
                        cat.TnP_amount= req.POST['Dept_amount']
                        cat.save()
                        print(444)
                    else:
                        print(dept)
                        cat = NoDues_application_table.objects.get(pk=req.POST['idbb'])
                        cat.EnrollmentId = req.POST['EnrollmentId']
                        cat.Name = req.POST['Name']
                        cat.Dept_approval = req.POST['Dept_approval']
                        cat.Dept_Comment= req.POST['Dept_comment']
                        cat.save()
                        print(444)

        else:
                    cat = Application_table.objects.get(pk=req.POST.get('idbb'))
                    cat.delete()
        return redirect('/api/adminDash')
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
            print("huihuihuihui")
            if req.session['Enrollment'] == '':
                return redirect('/')
            enr = req.session['Enrollment']
            qry = "select * from nocrest_student where EnrollmentId = '{0}'".format(enr)
            cursor = connection.cursor()
            cursor.execute(qry)
            rec = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(rec)
            print(rec['Branch'])
            passW = check_password(req.session['StudPass'],rec['password']) 
            print("dgkjbgiu",passW)
            print(req.session['StudPass'])
            print(rec['password'])
            rec['password'] = req.session['StudPass']
            qry = "select Department_name from nocrest_department where Dep_Id={0}".format(rec['Branch'])
            cursor = connection.cursor()
            cursor.execute(qry)
            r = tuple_to_dict.ParseDictSingleRecord(cursor)
            print(r['Department_name'])
            dept = r['Department_name']
            return render(req, 'Profile.html',{'record':rec ,'branchstud':dept})
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
    if(req.session['Ad_Status'] == 'passive'):
                return
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
        
@api_view(['GET', 'POST', 'DELETE'])
def ExitShowSurvey(req):
    # if(req.session['Ad_Status'] == 'passive'):
    #             return
    try:
            # if req.session['Adminemail'] == '':
            #     print("session khali")
            #     return redirect('/')
            qry = "select * from nocrest_exitsurvey"
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
            # if(req.session['Ad_Status'] == 'passive'):
            #     return
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
            # if(req.session['Ad_Status'] == 'passive'):
            #     return
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
            if(req.session['Ad_Status'] == 'passive'):
                return
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
            if(req.session['Ad_Status'] == 'passive'):
                return
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
                rec['Password'] = req.session['AdminPass']
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
from django.core.files.uploadedfile import SimpleUploadedFile
@api_view(['GET', 'POST', 'DELETE'])
def StudentEdit(request):
    try:
        if request.method == 'POST':
            father = request.POST.get('fathers_name')
            address = request.POST.get('Address')
            contact = request.POST.get('contact_Num')
            dept = request.POST.get('Branch')
            password = request.POST.get('password')
            student_id = request.POST.get('idbb')
            enroll = request.POST.get('EnrollmentId')
            name = request.POST.get('Name')
            PassW = make_password(password)
            student = Student.objects.get(pk=student_id)
            student.fathers_name = father
            student.Address = address
            student.contact_Num = contact
            student.Branch = dept
            student.password = PassW

            if 'image' in request.FILES:
                image = request.FILES['image']
                # Get file extension
                _, extension = os.path.splitext(image.name)
                # Create new filename
                new_filename = f'student_images/{enroll}{name}{extension}'
                
                # Create a new SimpleUploadedFile with the new filename
                new_image = SimpleUploadedFile(
                    new_filename,
                    image.read(),
                    content_type=image.content_type
                )
                # Assign the new image to the student
                student.image = new_image
        
            student.save()
            request.session['StudPass'] = password

        return redirect('/api/studentlogin')


            # return redirect('/api/studentlogin')
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
            PassW = make_password(passs)
            student_id = req.POST.get('idbb')
            student = Admins.objects.get(pk=student_id)
            student.Email = email
            student.Contact = contact
            student.dept = dep
            student.Password = PassW
            student.save()
            req.session['AdminPass'] = passs
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
            data = Admins.objects.get(pk=row_id)
            data.delete()
            return redirect('/api/superadmin')
    except Exception as e:
        print("Error", e)
@api_view(['GET'])
def StDelete(request):
    try:
        if request.method == 'GET':
            # Get the ID from query parameters
            row_id = request.query_params.get('id')
            print(row_id)
            data = Student.objects.get(pk=row_id)
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
        # ADname = req.session['Adminname']
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

        return render(req, "Super.html",{"data":num,"nocdata":nocnum,"noctnp":noctnp,"nod":nod,"nodapp":noduapp,"name":'ADname'})
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


from django.views.decorators.http import require_POST
@require_POST
def give_nodues(request):
    enrollment_id = request.POST.get('enroll')
    id = request.POST.get('idbb')
    comm = request.POST.get('Acc_comment')
    print(enrollment_id,id,comm)
    cat = NoDues_application_table.objects.get(pk=request.POST['idbb'])
    cat.Acc_approval = 'Approved'
    cat.Acc_Comment = comm
    cat.save()
    return redirect('/api/adminDash?clicked=9')

    # return redirect('/')
    # print(f"Processing No Dues approval for EnrollmentId: {enrollment_id}")
    
    # # Here you would typically update the database
    # # For example: Student.objects.filter(EnrollmentId=enrollment_id).update(no_dues_status=True)
    
    # return JsonResponse({
    #     'status': 'success',
    #     'message': f'No Dues given to student with EnrollmentId: {enrollment_id}'
    # })
