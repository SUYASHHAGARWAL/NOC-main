from rest_framework import serializers
from nocrest.models import Student
from nocrest.models import Department
from nocrest.models import Admins
from nocrest.models import Application_table
from nocrest.models import NoDues_application_table
from nocrest.models import Graduated
from nocrest.models import InternshipFeedback
from nocrest.models import BonafideModel
from nocrest.models import ExitSurvey

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
        fields = ('id','Role','Email','dept','Contact','Password','admin_id','status','name','signature')

class adminserialiser(serializers.ModelSerializer):
    class Meta:
        model = Application_table
        fields = ('id','EnrollmentId','Name','Email','dept','year','Company','location','name_reciever','Designation_reciever','duration','startDate','endDate','org_address','websitr_org','apply_through','offerletter','stipend','declaration','App_Id','Dept_approval','Dept_Comment','TnP_approval','TnP_Comment','App_Date','App_time','Time_Dept_approval','Time_Tnp_approval','allow_edit')

class noduesserialiser(serializers.ModelSerializer):
    class Meta:
        model = NoDues_application_table
        fields = ('id','EnrollmentId','Name','Email','dept','App_Id','Dept_approval','Dept_Comment','TnP_approval','TnP_Comment','Lib_approval','Lib_Comment','Acc_approval','Acc_Comment','Hostle_approval','Hostle_Comment','Exam_approval','Exam_Comment','App_Date','App_time','account_holder_name','bank_name','account_number','ifsc_code','dob','passOutYear','hostel','fees_due','project_report','caution_money',)

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

class ExitSuevrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExitSurvey
        fields = [
            'id',
            'Name',
            'EnrollmentId',
            'Email',
            'Department',
            'Phone',
            'Apply',
            'DOB',
            'Gender',
            'Course',
            'Branch',
            'RateFaculty',
            'TeachingMethods',
            'LearningResources',
            'SyllabusCompletion',
            'CourseRelevance',
            'TeacherPreparedness',
            'CourseOutcomes',
            'SoftSkills',
            'InternshipsSupport',
            'StudentOrgs',
            'CurricularExtracurricular',
            'Quizzes',
            'EvaluationFairness',
            'LibraryResources',
            'CurriculumFlexibility',
            'NPTELMOOCs',
            'FullSemesterInternship',
            'TrainingPlacement',
            'InternshipCompany',
            'InternshipCertificate',
            'JobSelection',
            'OutsideJobOffer',
            'OutsideJobLetter',
            'MultipleOfferCompanies',
            'MultipleOfferLetters',
            'OptedJoborPG',
            'FurtherStudyDetails',
            'JoiningCompany',
            'QualifiedGate',
            'GateRank',
            'GateScorecard',
            'AppearedForExams',
            'OtherExamName',
            'ScoreCardsAll',
            'Percentile',
            'MTechUniversity',
            'MBACollege',
            'AdmissionLetter',
            'AnyOtherCompetitiveExams',
            'DonateCautionMoney',
            'FinalSemesterChoice',
            'FinalYearInternship',
            'FinalInternshipStipend',
            'FinalInternshipStipendAmount',
            'InternshipCompanyProcess',
            'JobOfferExtension',
            'FinalSemesterInternshipDoc',
            'PermanentEmail',
            'ContactNum',
            'ParentContactNum',
            'HomeTown',
            'PermanentAddress',
            'Suggestions',
            'AppDate',
            'AppTime']