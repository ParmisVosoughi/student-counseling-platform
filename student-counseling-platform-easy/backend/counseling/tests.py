import os
os.environ.setdefault('USE_SQLITE','True')
from datetime import date,timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User,SupervisorProfile,AdvisorProfile
from .models import Student,WeeklyPerformance,AssessmentResult,StudentChallenge,ProgramLogicCategory,ProgramLogicReview,ProgramLogicReviewStatusHistory

class WorkflowPermissionTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create_user('admin','admin@test.local','StrongPass123!',role='ADMIN')
        self.s1=User.objects.create_user('s1','s1@test.local','StrongPass123!',role='SUPERVISOR'); SupervisorProfile.objects.create(user=self.s1)
        self.s2=User.objects.create_user('s2','s2@test.local','StrongPass123!',role='SUPERVISOR'); SupervisorProfile.objects.create(user=self.s2)
        self.a1=User.objects.create_user('a1','a1@test.local','StrongPass123!',role='ADVISOR'); AdvisorProfile.objects.create(user=self.a1,supervisor=self.s1)
        self.a2=User.objects.create_user('a2','a2@test.local','StrongPass123!',role='ADVISOR'); AdvisorProfile.objects.create(user=self.a2,supervisor=self.s2)
        self.st1=Student.objects.create(advisor=self.a1,first_name='A',last_name='One',student_code='S001',enrollment_date=date.today())
        self.st2=Student.objects.create(advisor=self.a2,first_name='B',last_name='Two',student_code='S002',enrollment_date=date.today())
        self.client=APIClient()
    def auth(self,u): self.client.force_authenticate(u)
    def test_advisor_cannot_access_other_student(self):
        self.auth(self.a1); self.assertEqual(self.client.get(f'/api/students/{self.st2.id}/').status_code,404)
    def test_supervisor_cannot_access_other_team(self):
        self.auth(self.s1); self.assertEqual(self.client.get(f'/api/students/{self.st2.id}/').status_code,404)
    def test_admin_can_access_all(self):
        self.auth(self.admin); self.assertEqual(self.client.get(f'/api/students/{self.st2.id}/').status_code,200)
    def test_advisor_can_create_student_for_self(self):
        self.auth(self.a1)
        r=self.client.post('/api/students/',{'first_name':'C','last_name':'Three','student_code':'S003','enrollment_date':str(date.today()),'status':'ACTIVE'},format='json')
        self.assertEqual(r.status_code,201); self.assertEqual(Student.objects.get(student_code='S003').advisor,self.a1)
    def test_weekly_creation_and_duplicate_validation(self):
        self.auth(self.a1); payload={'student':self.st1.id,'week_start':str(date.today()),'total_study_hours':'12.5','test_questions':100,'written_questions':20}
        self.assertEqual(self.client.post('/api/weekly-performance/',payload,format='json').status_code,201)
        self.assertEqual(self.client.post('/api/weekly-performance/',payload,format='json').status_code,400)
    def test_assessment_dynamic_parameters(self):
        self.auth(self.a1); payload={'student':self.st1.id,'assessment_name':'External Test','assessment_date':str(date.today()),'overall_score':'75','parameters':[{'parameter_name':'Focus','value':'71','display_order':1},{'parameter_name':'Motivation','value':'80','display_order':2}]}
        r=self.client.post('/api/assessment-results/',payload,format='json'); self.assertEqual(r.status_code,201); self.assertEqual(AssessmentResult.objects.get(pk=r.data['id']).parameters.count(),2)
    def test_challenge_workflow(self):
        self.auth(self.a1); payload={'student':self.st1.id,'title':'Issue','category':'Custom','description':'Details','severity':'HIGH','status':'OPEN','date_identified':str(date.today())}
        r=self.client.post('/api/challenges/',payload,format='json'); self.assertEqual(r.status_code,201)
        r2=self.client.patch(f"/api/challenges/{r.data['id']}/",{'status':'RESOLVED','resolved_date':str(date.today()),'resolution_notes':'Done'},format='json'); self.assertEqual(r2.status_code,200)
    def test_supervisor_program_review_and_advisor_implementation(self):
        cat=ProgramLogicCategory.objects.create(name='توزیع ساعت مطالعه')
        self.auth(self.s1); payload={'advisor':self.a1.id,'student':self.st1.id,'review_date':str(date.today()),'overall_quality_rating':3,'error_severity':'MODERATE','error_category_ids':[cat.id],'problem_description':'Problem','incorrect_logic_location':'Week plan','recommended_solution':'Fix distribution','implementation_status':'AWAITING_IMPLEMENTATION'}
        r=self.client.post('/api/program-reviews/',payload,format='json'); self.assertEqual(r.status_code,201)
        self.auth(self.a1); r2=self.client.patch(f"/api/program-reviews/{r.data['id']}/",{'implementation_status':'IMPLEMENTED','advisor_implementation_notes':'Applied','date_implemented':str(date.today())},format='json')
        self.assertEqual(r2.status_code,200); self.assertEqual(ProgramLogicReview.objects.get(pk=r.data['id']).implementation_status,'IMPLEMENTED'); self.assertEqual(ProgramLogicReviewStatusHistory.objects.filter(review_id=r.data['id']).count(),2)
    def test_advisor_cannot_edit_supervisor_fields(self):
        r=ProgramLogicReview.objects.create(supervisor=self.s1,advisor=self.a1,student=self.st1,review_date=date.today(),overall_quality_rating=3,error_severity='MINOR')
        self.auth(self.a1); resp=self.client.patch(f'/api/program-reviews/{r.id}/',{'problem_description':'Tampered'},format='json'); self.assertEqual(resp.status_code,403)
