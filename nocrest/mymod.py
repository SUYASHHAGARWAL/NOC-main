from django.db import models

# Create your models here.
class Student(models.Model):
    EnrollmentId = models.CharField(max_length=120,blank=False)
    Name = models.CharField(max_length=120,blank=False)
    fathers_name = models.CharField(max_length=120,blank=False)
    Address = models.CharField(max_length=120,blank=False)
    contact_Num = models.CharField(max_length=120,blank=False)
    Email = models.CharField(max_length=120,blank=False)
    Branch = models.CharField(max_length=120,blank=False)
    Noc_Count = models.CharField(max_length=120,blank=False, default=0)
    password = models.CharField(max_length=255,blank=False, default=0)
    username = models.CharField(max_length=120,blank=False, default=0)
    Email_personal = models.CharField(max_length=120,blank=False, default=0)
    image = models.ImageField(upload_to='student_images/', null=True, blank=True)

class Department(models.Model):
    Dep_Id = models.CharField(max_length=120,blank=False,default='')
    Department_name = models.CharField(max_length=120,blank=False,default='')
    Department = models.CharField(max_length=120,blank=False,default='')
    programmme = models.CharField(max_length=20,blank=False,default='')
    Displayname = models.CharField(max_length=50,blank=False, default='')

class Admins(models.Model):
    Role = models.CharField(max_length=100,blank=False,default='')
    name = models.CharField(max_length=100,blank=False,default='')
    Email = models.CharField(max_length=50,blank=False,default='')
    dept = models.CharField(max_length=120,blank=False,default='')
    Contact = models.CharField(max_length=12,blank=False,default='')
    Password = models.CharField(max_length=255,blank=False,default='')
    admin_id = models.CharField(max_length=15,blank=False,default='')
    status = models.CharField(max_length=15,blank=False,default='')
    signature = models.CharField(max_length=255)#Abstractuser table 
    
class Application_table(models.Model):
    EnrollmentId = models.CharField(max_length=12, blank=False, default='')
    Name = models.CharField(max_length=50, blank=False, default='')
    Email = models.CharField(max_length=35, blank=False, default='')
    dept = models.CharField(max_length=120, blank=False, default='')
    year = models.CharField(max_length=35, blank=False, default='')
    Company = models.CharField(max_length=35, blank=False, default='')
    location = models.CharField(max_length=35, blank=False, default='')
    name_reciever = models.CharField(max_length=60, blank=False, default='')
    Designation_reciever = models.CharField(max_length=60, blank=False, default='')
    duration = models.CharField(max_length=40, blank=False, default='')
    startDate = models.CharField(max_length=40, blank=False, default='')
    endDate = models.CharField(max_length=40, blank=False, default='')
    org_address = models.CharField(max_length=150, blank=False, default='')
    websitr_org = models.CharField(max_length=150, blank=False, default='')
    apply_through = models.CharField(max_length=150, blank=False, default='')
    offerletter = models.FileField(upload_to='static/')
    stipend = models.CharField(max_length=150, blank=False, default='')
    declaration = models.CharField(max_length=150, blank=False, default='')
    Role = models.CharField(max_length=35, blank=False, default='-')
    App_Id = models.CharField(max_length=12, blank=False, default='')
    Dept_approval = models.CharField(max_length=12, blank=False, default='')
    Dept_Comment = models.CharField(max_length=100, blank=False, default='')
    TnP_approval = models.CharField(max_length=12, blank=False, default='')
    TnP_Comment = models.CharField(max_length=100, blank=False, default='')
    App_Date = models.CharField(max_length=100, blank=False, default='')
    App_time = models.CharField(max_length=100, blank=False, default='')
    Time_Dept_approval = models.CharField(max_length=100, blank=False, default='')
    Time_Tnp_approval = models.CharField(max_length=100, blank=False, default='')
    date_dept_approval = models.CharField(max_length=100, blank=False, default='')
    date_tnp_approval = models.CharField(max_length=100, blank=False, default='')
    noc = models.CharField(max_length=100, blank=False, default='')
    D_approved_by = models.CharField(max_length=150, blank=False, default='')
    Tnp_approved_by = models.CharField(max_length=150, blank=False, default='')
    allow_edit = models.CharField(max_length=12,blank=False, default='')
    
class NoDues_application_table(models.Model):
    EnrollmentId = models.CharField(max_length=12,blank=False,default='')
    Name = models.CharField(max_length=50,blank=False,default='')
    Email = models.CharField(max_length=35,blank=False,default='')
    dept = models.CharField(max_length=35,blank=False,default='')
    App_Id = models.CharField(max_length=12,blank=False,default='')
    Dept_approval = models.CharField(max_length=12,blank=False,default='')
    Dept_Comment = models.CharField(max_length=100,blank=False,default='')
    Dept_amount = models.CharField(max_length=100,blank=False,default='')
    TnP_approval = models.CharField(max_length=12,blank=False,default='')
    TnP_Comment = models.CharField(max_length=100,blank=False,default='')
    TnP_amount = models.CharField(max_length=100,blank=False,default='')
    Lib_approval = models.CharField(max_length=12,blank=False,default='')
    Lib_Comment = models.CharField(max_length=100,blank=False,default='')
    Lib_amount = models.CharField(max_length=100,blank=False,default='')
    Acc_approval = models.CharField(max_length=12,blank=False,default='')
    Acc_Comment = models.CharField(max_length=100,blank=False,default='')
    Hostle_approval = models.CharField(max_length=12,blank=False,default='')
    Hostle_Comment = models.CharField(max_length=100,blank=False,default='')
    Hostle_amount = models.CharField(max_length=100,blank=False,default='')
    Exam_approval = models.CharField(max_length=12,blank=False,default='')
    Exam_Comment = models.CharField(max_length=100,blank=False,default='')
    Exam_amount = models.CharField(max_length=100,blank=False,default='')
    Genoffice_approval = models.CharField(max_length=12,blank=False,default='')
    Genoffice_Comment = models.CharField(max_length=100,blank=False,default='')
    Genoffice_amount = models.CharField(max_length=100,blank=False,default='')
    App_Date = models.CharField(max_length=100,blank=False,default='')
    App_time = models.CharField(max_length=100,blank=False,default='')
    account_holder_name = models.CharField(max_length=100, blank=False, default='')
    bank_name = models.CharField(max_length=100, blank=False, default='')
    account_number = models.CharField(max_length=20, blank=False, default='')
    ifsc_code = models.CharField(max_length=20, blank=False, default='')
    dob = models.CharField(max_length=20, blank=False, default='')
    passOutYear = models.CharField(max_length=20, blank=False, default='')
    hostel = models.CharField(max_length=3, blank=False, default='')
    fees_due = models.CharField(max_length=3, blank=False, default='')
    project_report = models.CharField(max_length=3, blank=False, default='')
    caution_money = models.CharField(max_length=3, blank=False, default='')

class Graduated(models.Model):
    EnrollmentId = models.CharField(max_length=12,blank=False,default='',unique=True)
    Name = models.CharField(max_length=60,blank=False,default='')

class InternshipFeedback(models.Model):
    intern_enrollment_id = models.CharField(max_length=15, blank=False, default='')
    department = models.CharField(max_length=35, blank=False, default='')
    noc_approval_id = models.CharField(max_length=35,blank=False, default='')
    company_name = models.CharField(max_length = 35, blank=False, default = '')
    company_experience_rating = models.CharField(max_length=35,default='')
    work_environment_rating = models.CharField(max_length=35,default='')
    supervisor_rating = models.CharField(max_length=35,default='')
    comments = models.TextField(blank=True)
    hr_name = models.EmailField(max_length=35, blank=False, default='')
    hr_contact_email = models.EmailField(max_length=35, blank=False, default='')
    hr_contact_number = models.CharField(max_length=15, blank=True, default='')

class BonafideModel(models.Model):
    student_name = models.CharField(max_length=50, blank=False, default='')
    EnrollmentId = models.CharField(max_length=50, blank=False, default='')
    fathers_name = models.CharField(max_length=50, blank=False, default='')
    Semester = models.CharField(max_length=50, blank=False, default='')
    email = models.CharField(max_length=50, blank=False, default='')
    session = models.CharField(max_length=50, blank=False, default='')
    application_date = models.CharField(max_length=20, blank=False, default='')
    approval_date = models.CharField(max_length=20, blank=False, default='')
    app_id = models.CharField(max_length=20, blank=False, default='')
    dept_approval = models.CharField(max_length=20, blank=False, default='')
    dept_comment = models.CharField(max_length=20, blank=False, default='')
    Branch = models.CharField(max_length=50, blank=False, default='')
    bonafide = models.CharField(max_length=100, blank=False, default='')

    
class ExitSurvey(models.Model):
    Name = models.CharField(max_length=120, default='')
    EnrollmentId = models.CharField(max_length=120, default='')
    Email = models.EmailField(max_length=254,default='')
    Department = models.CharField(max_length=120, default='')
    Phone = models.CharField(max_length=15,  default='')
    Apply = models.CharField(max_length=10,  default='Yes')
    DOB = models.DateField(blank=False)
    Gender = models.CharField(max_length=10, default='')
    Course = models.CharField(max_length=50,  default='')
    Branch = models.CharField(max_length=120,default='')
    RateFaculty = models.IntegerField(default=0)
    TeachingMethods = models.TextField(default='')
    TeachingEngagement = models.TextField( default='')
    SyllabusCompletion = models.TextField( default='')
    CourseRelevance = models.TextField(default='')
    TeacherPreparedness = models.TextField( default='')
    CourseOutcomes = models.TextField( default='')
    SoftSkills = models.TextField( default='')
    InternshipsSupport = models.TextField( default='')
    StudentOrgs = models.TextField( default='')
    CurricularExtracurricular = models.TextField( default='')
    Quizzes = models.TextField( default='')
    EvaluationFairness = models.TextField(default='')
    LibraryResources = models.TextField( default='')
    CurriculumFlexibility = models.TextField( default='')
    NPTELMOOCs = models.TextField(default='')
    FullSemesterInternship = models.TextField( default='')
    TrainingPlacement = models.TextField(default='')
    InternshipCompany = models.TextField( default='')
    InternshipCertificate = models.TextField( default='')
    JobSelection = models.TextField( default='')
    OutsideJobOffer = models.TextField( default='')
    OutsideJobLetter = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    offer_letter_1 = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    offer_letter_2 = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    offer_letter_3 = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    offer_letter_4 = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    offer_letter_5 = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    MultipleOfferCompanies = models.TextField( default='')
    MultipleOfferLetters = models.FileField( default='')
    OptedJoborPG = models.TextField(default='')
    FurtherStudyDetails = models.TextField( default='')  # Adjusted field name
    JoiningCompany = models.TextField(default='')  # Adjusted field name
    QualifiedGate = models.TextField( default='')
    GateRank = models.TextField(default='')  # Adjusted field name
    GateScorecard = models.FileField(upload_to='gate_scorecards/', null=True, blank=True)
    AppearedForExams = models.TextField( default='')
    OtherExamName = models.TextField( default='')  # Adjusted field name
    ScoreCardsAll = models.FileField(upload_to='entrance_exam_scorecards/', null=True, blank=True)
    Percentile = models.TextField( default='')  # Adjusted field name
    MTechUniversity = models.TextField( default='')  # Adjusted field name
    MBACollege = models.TextField( default='')  # Adjusted field name
    AdmissionLetter = models.FileField(upload_to='higher_education_documents/', null=True, blank=True)    
    AnyOtherCompetitiveExams = models.TextField( default='')  # Adjusted field name
    DonateCautionMoney = models.TextField( default='')
    FinalSemesterChoice = models.TextField( default='')
    FinalYearInternship = models.TextField(default='')  # Adjusted field name
    FinalInternshipStipend = models.TextField( default='')  # Adjusted field name
    FinalInternshipStipendAmount = models.TextField( default='')  # Adjusted field name
    StipendDocProof = models.TextField( default='')  # Adjusted field name
    InternshipCompanyProcess = models.TextField( default='')
    JobOfferExtension = models.TextField( default='')  # Adjusted field name
    FinalSemesterInternshipDoc = models.FileField(upload_to='final_semester_documents/', null=True, blank=True)
    PermanentEmail = models.EmailField( default='')  # Adjusted field type and name
    ContactNum = models.TextField( default='')
    ParentContactNum = models.TextField( default='')
    HomeTown = models.TextField( default='')
    PermanentAddress = models.TextField( default='')
    Suggestions = models.TextField( default='') 
    AppDate = models.DateField(auto_now_add=True)
    AppTime = models.TimeField(auto_now_add=True)