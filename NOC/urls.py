"""
URL configuration for NOC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from nocrest.views import upload_file
from django.conf.urls.static import static


from nocrest import views
from nocrest.views import home, login, custom_logout, view_logs

urlpatterns = [

    path('your_django_upload_view/', upload_file, name='upload_file'),
    path('logs-5gx52/', view_logs, name='view_logs'),
    path('admin/', admin.site.urls),
        # path('accounts/', include('allauth.urls')),
            path('auth/', include('social_django.urls', namespace='social')),
path('home/', home, name='home'),
    path('login/', login, name='login'),
path('logout/', custom_logout, name='logout'),
    path('', views.Frontpage),
    # path('main', views.login_google),
    # path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    # path ('auth/' , include ('social_django.urls' , namespace='social')),
    path ('verifyNOC/' , views.verify_noc, name='search_view'),
    path ('pageverifyNOC/' , views.VerifyPage, name='search_view'),
    path ('67fgs47dg/' , views.trigger_pull),
    
    re_path(r'^api/frontpage',views.Frontpage),
    re_path(r'^logout/api/frontpage',views.Frontpage),
    re_path(r'^api/adminfp',views.Deptfp),
    re_path(r'^api/tnpfp',views.Tnpfp),
# path('offerupload/', offer_upload_view, name='upload_offer_letter'),
    path('submit_application/', views.SubmitApplication, name='your_submit_application_url'),
    re_path(r'^api/adminDash',views.DashLogin),
    re_path(r'^api/adminlogin',views.DeptLogin),
    re_path(r'^api/dashboard',views.Dashboard),
    re_path(r'^api/studentlogin',views.StudentLogin),
    re_path(r'^api/registerstuds',views.StudentREg),
    re_path(r'^api/adminregister',views.AdminREg),
    re_path(r'^api/adsignup',views.Adsignup),
    # re_path(r'^api/Tnplogin',views.TnPLogin),
    re_path(r'^api/ApplyBonafied',views.ApplyBonafide),
    re_path(r'^api/submitapplication',views.SubmitApplication),
    re_path(r'^api/submitnoduesapp',views.SubmitNoDuesApp),
    re_path(r'^api/checkstdprevapp',views.ChekPreviousApp),
    re_path(r'^api/bonafstatus',views.BonafStatus),
    re_path(r'^api/fetchfradstudents',views.ShowGradStuds),
    re_path(r'^api/Noduesstatus',views.NoduesStatus),
    re_path(r'^api/appliedstudents',views.ShowAppliedstudent),
    re_path(r'^api/ndapliedstudents',views.NoDuesAppliedstudent),
    # re_path(r'^api/appliedbydept',views.ShowdeptAppliedstudent),
    re_path(r'^api/editapplication',views.EditApplication),
    re_path(r'^api/NDapplicationedit',views.NDApplicationedit),
    re_path(r'^api/editFacluty',views.EditFAculty),
    re_path(r'^api/approval',views.Approval),

    # re_path(r'^api/edittnpapplication',views.EditTnpApplication),
    re_path(r'^api/editsavedept',views.EditSaveDept),
    re_path(r'^api/AdminApproval',views.AdminApproval),
    re_path(r'^api/editbonafide',views.BonaEdit),
    re_path(r'^api/statussave',views.Status),
    re_path(r'^api/editsavenddept',views.EditSaveNDDept),
    re_path(r'^api/editsavetnp',views.EditSaveTnp),
    re_path(r'^api/apliedstudentswhoapproved',views.AppliedStudeApproved),
    re_path(r'^api/aplieddisapprovedstudents',views.AppliedDisapprovedStud),
    re_path(r'^api/ndapprovedstudents',views.NDapproved),
    re_path(r'^api/dashadmin',views.DashAdmin),

    re_path(r'^api/internshipfeedback',views.InternFeedback),
    re_path(r'^api/studentdataedit',views.StudentEdit),
    re_path(r'^api/admindataedit',views.adminEdit),
    re_path(r'^api/studentprofile',views.StudentProfile),
    re_path(r'^api/Fedbackform',views.FeedbackForm),
    re_path(r'^api/adminprofile',views.AdminProfile),
    re_path(r'^api/companydata',views.Companydata),
    re_path(r'^api/adminfaculties',views.AdminFaculties),
    re_path(r'^api/adminroles',views.AdminRoles),
    re_path(r'^api/admincheckstudents',views.AdminStudents),
    re_path(r'^api/adminnocstudents',views.AdminNOCstuds),
    re_path(r'^api/adminnoduestudents',views.AdminNoDuesstuds),
    re_path(r'^api/adminhostle',views.AdminHostle),
    re_path(r'^api/superadmin',views.SuperAdmin),
    re_path(r'^api/showfeedback',views.ShowFeedback),
    re_path(r'^api/AllApplications',views.AllApplications),
    re_path(r'^api/BonafApplications',views.BonafApplications),
    re_path(r'^api/A_prpprovedBonafides',views.ApprovedBonafApplications),
    re_path(r'^api/D_eclineddBonafides',views.DeclinedBonafApplications),
    re_path(r'^api/StudsFeedBack',views.StudentFeedback),
    re_path(r'^api/show_feedback',views.FeedbackByStudents),
    re_path(r'^api/ALldepartments',views.ShowDepartments),
    re_path(r'^api/DelFaculty',views.FDelete),
    re_path(r'^api/editAppNocStud',views.NOCEditApp),
    re_path(r'^api/Edit_dept_admin',views.EditDeptAdmin),
    re_path(r'^api/PaddDEPT',views.AddDeptAdmin),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
