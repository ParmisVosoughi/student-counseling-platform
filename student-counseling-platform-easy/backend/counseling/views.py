from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Student, WeeklyPerformance, AssessmentResult, StudentChallenge, ProgramLogicCategory, ProgramLogicReview, ProgramLogicReviewStatusHistory, Activity
from .serializers import StudentSerializer, WeeklyPerformanceSerializer, AssessmentResultSerializer, StudentChallengeSerializer, ProgramLogicCategorySerializer, ProgramLogicReviewSerializer, ActivitySerializer
from .access import students_for, advisors_for

class ScopedModelViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','put','patch','delete','head','options']
    def destroy(self,request,*args,**kwargs):
        return Response({'detail':'حذف دائمی این رکورد مجاز نیست. از وضعیت/بایگانی استفاده کنید.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)

class StudentViewSet(ScopedModelViewSet):
    serializer_class=StudentSerializer
    def get_queryset(self):
        qs=students_for(self.request.user).order_by('-created_at')
        q=self.request.query_params.get('search'); status_=self.request.query_params.get('status'); advisor=self.request.query_params.get('advisor'); supervisor=self.request.query_params.get('supervisor')
        if q: qs=qs.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(student_code__icontains=q))
        if status_: qs=qs.filter(status=status_)
        if advisor: qs=qs.filter(advisor_id=advisor)
        if supervisor and self.request.user.role=='ADMIN': qs=qs.filter(advisor__advisor_profile__supervisor_id=supervisor)
        return qs
    def perform_create(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر مجاز به ایجاد دانش‌آموز نیست.')
        if self.request.user.role=='ADVISOR': s.save(advisor=self.request.user); student=s.instance
        else: s.save(); student=s.instance
        Activity.objects.create(actor=self.request.user,student=student,advisor=student.advisor,activity_type='STUDENT_ADDED',description='دانش‌آموز جدید ثبت شد.')
    def perform_update(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر فقط مجاز به مشاهده اطلاعات دانش‌آموز است.')
        s.save()
    @action(detail=True,methods=['post'])
    def archive(self,request,pk=None):
        if request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر مجاز به بایگانی دانش‌آموز نیست.')
        obj=self.get_object(); obj.status='ARCHIVED'; obj.save(update_fields=['status','updated_at']); return Response(StudentSerializer(obj,context={'request':request}).data)

class WeeklyPerformanceViewSet(ScopedModelViewSet):
    serializer_class=WeeklyPerformanceSerializer
    def get_queryset(self):
        qs=WeeklyPerformance.objects.filter(student__in=students_for(self.request.user)).select_related('student').order_by('-week_start')
        if s:=self.request.query_params.get('student'): qs=qs.filter(student_id=s)
        return qs
    def perform_create(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ثبت عملکرد هفتگی توسط مشاور انجام می‌شود.')
        s.save(created_by=self.request.user,updated_by=self.request.user); o=s.instance
        Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.student.advisor,activity_type='WEEKLY_CREATED',description='عملکرد هفتگی ثبت شد.')
    def perform_update(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر فقط مجاز به مشاهده این رکورد است.')
        s.save(updated_by=self.request.user)

class AssessmentResultViewSet(ScopedModelViewSet):
    serializer_class=AssessmentResultSerializer
    def get_queryset(self):
        qs=AssessmentResult.objects.filter(student__in=students_for(self.request.user)).prefetch_related('parameters').order_by('-assessment_date')
        if s:=self.request.query_params.get('student'): qs=qs.filter(student_id=s)
        if name:=self.request.query_params.get('assessment_name'): qs=qs.filter(assessment_name__icontains=name)
        if v:=self.request.query_params.get('date_from'): qs=qs.filter(assessment_date__gte=v)
        if v:=self.request.query_params.get('date_to'): qs=qs.filter(assessment_date__lte=v)
        return qs
    def perform_create(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ثبت نتیجه ارزیابی توسط مشاور انجام می‌شود.')
        s.save(created_by=self.request.user,updated_by=self.request.user); o=s.instance
        Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.student.advisor,activity_type='ASSESSMENT_CREATED',description=f'نتیجه ارزیابی «{o.assessment_name}» ثبت شد.')
    def perform_update(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر فقط مجاز به مشاهده این رکورد است.')
        s.save(updated_by=self.request.user)

class StudentChallengeViewSet(ScopedModelViewSet):
    serializer_class=StudentChallengeSerializer
    def get_queryset(self):
        qs=StudentChallenge.objects.filter(student__in=students_for(self.request.user)).select_related('student').order_by('-date_identified')
        for key in ['student','severity','status','category']:
            if v:=self.request.query_params.get(key): qs=qs.filter(**{f'{key}_id' if key=='student' else key:v})
        return qs
    def perform_create(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ثبت چالش توسط مشاور انجام می‌شود.')
        s.save(created_by=self.request.user,updated_by=self.request.user); o=s.instance
        Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.student.advisor,activity_type='CHALLENGE_OPENED',description=f'چالش «{o.title}» ثبت شد.')
    def perform_update(self,s):
        if self.request.user.role=='SUPERVISOR': raise PermissionDenied('ناظر فقط مجاز به مشاهده این رکورد است.')
        old=self.get_object().status; s.save(updated_by=self.request.user); o=s.instance
        if old!='RESOLVED' and o.status=='RESOLVED': Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.student.advisor,activity_type='CHALLENGE_RESOLVED',description=f'چالش «{o.title}» حل شد.')

class ProgramLogicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=ProgramLogicCategorySerializer; pagination_class=None
    def get_queryset(self): return ProgramLogicCategory.objects.filter(is_active=True).order_by('name')

class ProgramLogicReviewViewSet(ScopedModelViewSet):
    serializer_class=ProgramLogicReviewSerializer
    def get_queryset(self):
        u=self.request.user; qs=ProgramLogicReview.objects.select_related('advisor','student','supervisor').prefetch_related('error_categories','status_history__changed_by')
        if u.role=='SUPERVISOR': qs=qs.filter(supervisor=u)
        elif u.role=='ADVISOR': qs=qs.filter(advisor=u)
        elif u.role!='ADMIN': qs=qs.none()
        if v:=self.request.query_params.get('advisor'): qs=qs.filter(advisor_id=v)
        if v:=self.request.query_params.get('student'): qs=qs.filter(student_id=v)
        if v:=self.request.query_params.get('error_severity'): qs=qs.filter(error_severity=v)
        if v:=self.request.query_params.get('implementation_status'): qs=qs.filter(implementation_status=v)
        if v:=self.request.query_params.get('date_from'): qs=qs.filter(review_date__gte=v)
        if v:=self.request.query_params.get('date_to'): qs=qs.filter(review_date__lte=v)
        return qs.order_by('-review_date')
    def perform_create(self,s):
        if self.request.user.role not in ['SUPERVISOR','ADMIN']: raise PermissionDenied('فقط ناظر یا مدیر می‌تواند بررسی برنامه ثبت کند.')
        supervisor=self.request.user if self.request.user.role=='SUPERVISOR' else s.validated_data.get('advisor').advisor_profile.supervisor
        s.save(supervisor=supervisor); o=s.instance
        ProgramLogicReviewStatusHistory.objects.create(review=o,status=o.implementation_status,changed_by=self.request.user,note='ایجاد بررسی')
        Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.advisor,activity_type='REVIEW_CREATED',description='بررسی منطق برنامه توسط ناظر ثبت شد.')
    def perform_update(self,s):
        if self.request.user.role=='ADVISOR':
            allowed={'implementation_status','advisor_implementation_notes','date_implemented'}
            if any(k not in allowed for k in s.validated_data.keys()): raise PermissionDenied('مشاور فقط می‌تواند وضعیت اجرا و یادداشت اجرای راهکار را تغییر دهد.')
            new_status=s.validated_data.get('implementation_status')
            if new_status and new_status not in ['AWAITING_IMPLEMENTATION','IMPLEMENTED','NOT_IMPLEMENTED']: raise PermissionDenied('این تغییر وضعیت برای مشاور مجاز نیست.')
        elif self.request.user.role not in ['SUPERVISOR','ADMIN']: raise PermissionDenied('دسترسی کافی ندارید.')
        old=self.get_object().implementation_status; s.save(); o=s.instance
        if old!=o.implementation_status: ProgramLogicReviewStatusHistory.objects.create(review=o,status=o.implementation_status,changed_by=self.request.user,note=o.advisor_implementation_notes[:300] if self.request.user.role=='ADVISOR' else o.supervisor_follow_up_notes[:300])
        if old!='IMPLEMENTED' and o.implementation_status=='IMPLEMENTED': Activity.objects.create(actor=self.request.user,student=o.student,advisor=o.advisor,activity_type='RECOMMENDATION_IMPLEMENTED',description='راهکار ناظر به‌عنوان اجراشده ثبت شد.')

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=ActivitySerializer
    def get_queryset(self):
        u=self.request.user; qs=Activity.objects.select_related('actor','student','advisor')
        if u.role=='ADMIN': pass
        elif u.role=='SUPERVISOR': qs=qs.filter(Q(advisor__advisor_profile__supervisor=u)|Q(actor=u))
        else: qs=qs.filter(Q(advisor=u)|Q(actor=u))
        if s:=self.request.query_params.get('student'): qs=qs.filter(student_id=s)
        return qs.order_by('-created_at')
