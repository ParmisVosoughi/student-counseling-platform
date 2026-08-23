from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from counseling.access import students_for, advisors_for
from counseling.models import Student,WeeklyPerformance,AssessmentResult,StudentChallenge,ProgramLogicReview,Activity
from accounts.models import User


def recent_change(records, field):
    vals=list(records.order_by('-week_start').values_list(field,flat=True)[:4])
    if len(vals)<2: return None
    latest=float(vals[0]); baseline=sum(float(x) for x in vals[1:])/len(vals[1:])
    if baseline==0: return None if latest==0 else 100.0
    return round((latest-baseline)/baseline*100,1)

def student_summary(student):
    weekly=student.weekly_performances.all()
    latest=weekly.order_by('-week_start').first()
    latest_assessment=student.assessment_results.order_by('-assessment_date').first()
    open_ch=student.challenges.exclude(status='RESOLVED')
    latest_review=student.program_reviews.order_by('-review_date').first()
    severity_rank={'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}
    highest=max((c.severity for c in open_ch),key=lambda x:severity_rank.get(x,0),default=None)
    return {
        'student_id':student.id,'student_name':str(student),
        'latest_weekly': {'week_start':latest.week_start,'study_hours':latest.total_study_hours,'test_questions':latest.test_questions,'written_questions':latest.written_questions} if latest else None,
        'changes': {'study_hours':recent_change(weekly,'total_study_hours'),'test_questions':recent_change(weekly,'test_questions'),'written_questions':recent_change(weekly,'written_questions')},
        'latest_assessment': {'name':latest_assessment.assessment_name,'date':latest_assessment.assessment_date,'overall_score':latest_assessment.overall_score} if latest_assessment else None,
        'open_challenges':open_ch.count(),'highest_severity_challenge':highest,
        'latest_review': {'id':latest_review.id,'severity':latest_review.error_severity,'status':latest_review.implementation_status,'recommendation':latest_review.recommended_solution} if latest_review else None,
    }

class SupervisorDashboardView(APIView):
    def get(self,request):
        if request.user.role not in ['SUPERVISOR','ADMIN']: raise PermissionDenied()
        advisors=advisors_for(request.user); students=students_for(request.user).filter(status='ACTIVE')
        reviews=ProgramLogicReview.objects.filter(advisor__in=advisors)
        challenges=StudentChallenge.objects.filter(student__in=students).exclude(status='RESOLVED')
        today=timezone.localdate(); cutoff=today-timedelta(days=14)
        attention=[]
        for s in students.select_related('advisor'):
            weekly=list(s.weekly_performances.order_by('-week_start')[:2]); reasons=[]
            if len(weekly)>=2 and float(weekly[1].total_study_hours)>0 and float(weekly[0].total_study_hours)<float(weekly[1].total_study_hours)*0.8: reasons.append('کاهش محسوس ساعت مطالعه')
            if len(weekly)>=2 and weekly[1].test_questions+weekly[1].written_questions>0 and weekly[0].test_questions+weekly[0].written_questions < (weekly[1].test_questions+weekly[1].written_questions)*0.8: reasons.append('کاهش محسوس حجم سؤال')
            if s.challenges.filter(severity__in=['HIGH','CRITICAL']).exclude(status='RESOLVED').exists(): reasons.append('چالش با شدت بالا')
            if s.program_reviews.exclude(implementation_status='IMPLEMENTED').exists(): reasons.append('بررسی/راهکار حل‌نشده')
            if reasons: attention.append({'id':s.id,'name':str(s),'advisor':s.advisor.get_full_name() or s.advisor.username,'reasons':reasons})
        overview=[]
        for a in advisors:
            astudents=students.filter(advisor=a); areviews=reviews.filter(advisor=a)
            overview.append({'id':a.id,'name':a.get_full_name() or a.username,'students':astudents.count(),'active_issues':challenges.filter(student__advisor=a).count(),'pending_recommendations':areviews.exclude(implementation_status='IMPLEMENTED').count(),'recent_activity':Activity.objects.filter(advisor=a,created_at__date__gte=cutoff).count()})
        return Response({'kpis':{'advisors':advisors.count(),'active_students':students.count(),'students_requiring_attention':len(attention),'unresolved_program_issues':reviews.exclude(implementation_status='IMPLEMENTED').count(),'implemented_recommendations':reviews.filter(implementation_status='IMPLEMENTED').count(),'pending_recommendations':reviews.filter(implementation_status__in=['ISSUE_IDENTIFIED','SOLUTION_PROVIDED','AWAITING_IMPLEMENTATION']).count()},'attention':attention[:20],'advisors':overview,'recent_activity':list(Activity.objects.filter(advisor__in=advisors).values('id','activity_type','description','created_at')[:10])})

class AdvisorDashboardView(APIView):
    def get(self,request):
        if request.user.role!='ADVISOR': raise PermissionDenied()
        students=students_for(request.user).filter(status='ACTIVE'); today=timezone.localdate(); week_start=today-timedelta(days=today.weekday())
        updated=WeeklyPerformance.objects.filter(student__in=students,week_start__gte=week_start).values('student').distinct().count()
        reviews=ProgramLogicReview.objects.filter(advisor=request.user)
        return Response({'kpis':{'active_students':students.count(),'updated_this_week':updated,'missing_weekly_updates':max(students.count()-updated,0),'open_challenges':StudentChallenge.objects.filter(student__in=students).exclude(status='RESOLVED').count(),'pending_recommendations':reviews.exclude(implementation_status='IMPLEMENTED').count(),'recent_assessments':AssessmentResult.objects.filter(student__in=students,assessment_date__gte=today-timedelta(days=30)).count()},'recent_activity':list(Activity.objects.filter(advisor=request.user).values('id','activity_type','description','created_at')[:10])})

class AdminDashboardView(APIView):
    def get(self,request):
        if request.user.role!='ADMIN': raise PermissionDenied()
        return Response({'kpis':{'users':User.objects.count(),'supervisors':User.objects.filter(role='SUPERVISOR',is_active=True).count(),'advisors':User.objects.filter(role='ADVISOR',is_active=True).count(),'students':Student.objects.filter(status='ACTIVE').count(),'open_challenges':StudentChallenge.objects.exclude(status='RESOLVED').count(),'pending_reviews':ProgramLogicReview.objects.exclude(implementation_status='IMPLEMENTED').count()},'recent_activity':list(Activity.objects.values('id','activity_type','description','created_at')[:10])})

class StudentSummaryView(APIView):
    def get(self,request,pk):
        student=students_for(request.user).filter(pk=pk).first()
        if not student: raise PermissionDenied('به این دانش‌آموز دسترسی ندارید.')
        return Response(student_summary(student))

class AdvisorSummaryView(APIView):
    def get(self,request,pk):
        advisor=advisors_for(request.user).filter(pk=pk).first()
        if not advisor: raise PermissionDenied('به این مشاور دسترسی ندارید.')
        students=Student.objects.filter(advisor=advisor,status='ACTIVE'); today=timezone.localdate(); week_start=today-timedelta(days=today.weekday())
        updated=WeeklyPerformance.objects.filter(student__in=students,week_start__gte=week_start).values('student').distinct().count(); reviews=ProgramLogicReview.objects.filter(advisor=advisor)
        return Response({'advisor_id':advisor.id,'advisor_name':advisor.get_full_name() or advisor.username,'active_students':students.count(),'regularly_updated':updated,'missing_weekly_updates':max(students.count()-updated,0),'open_challenges':StudentChallenge.objects.filter(student__in=students).exclude(status='RESOLVED').count(),'program_reviews':reviews.count(),'major_issues':reviews.filter(error_severity='MAJOR').count(),'recommendations':reviews.exclude(recommended_solution='').count(),'implemented_recommendations':reviews.filter(implementation_status='IMPLEMENTED').count(),'pending_recommendations':reviews.exclude(implementation_status='IMPLEMENTED').count(),'latest_review':reviews.values('id','review_date','error_severity','implementation_status').first()})
