from rest_framework import serializers
from nocrest.models import Student
from nocrest.models import Department
from nocrest.models import Admins
from nocrest.models import Application_table
from nocrest.models import NoDues_application_table
from nocrest.models import Graduated
from nocrest.models import InternshipFeedback
from nocrest.models import BonafideModel

class contactserialiser(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id','EnrollmentId','Name','fathers_name','Address','contact_Num','Email','Branch','Noc_Count','username','password')
    
class Newuserserialiser(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id','Dep_Id','Department_name','Department','programmme')

class Batchserialiser(serializers.ModelSerializer):
    class Meta:
        model = Admins
        fields = ('id','Role','Email','dept','Contact','Password','admin_id','status','name')

class adminserialiser(serializers.ModelSerializer):
    class Meta:
        model = Application_table
        fields = ('id','EnrollmentId','Name','Email','dept','year','Company','location','name_reciever','Designation_reciever','duration','startDate','endDate','org_address','websitr_org','apply_through','offerletter','stipend','declaration','App_Id','Dept_approval','Dept_Comment','TnP_approval','TnP_Comment','App_Date','App_time','Time_Dept_approval','Time_Tnp_approval','allow_edit')

class noduesserialiser(serializers.ModelSerializer):
    class Meta:
        model = NoDues_application_table
        fields = ('id','EnrollmentId','Name','Email','dept','App_Id','Dept_approval','Dept_Comment','TnP_approval','TnP_Comment','Lib_approval','Lib_Comment','Acc_approval','Acc_Comment','Hostle_approval','Hostle_Comment','App_Date','App_time')

class dataserialiser(serializers.ModelSerializer):
    class Meta:
        model = Graduated
        fields = ('id','EnrollmentId','Name')

class internfeedback(serializers.ModelSerializer):
    class Meta:
        model = InternshipFeedback
        fields = ('id','intern_enrollment_id','department','noc_approval_id','company_name','company_experience_rating','work_environment_rating','supervisor_rating','comments','hr_name','hr_contact_email','hr_contact_number')
 
class BonafideSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonafideModel
        fields = ('id','student_name','EnrollmentId','fathers_name','Semester','email','session','application_date','approval_date','app_id','dept_approval','dept_comment','Branch')