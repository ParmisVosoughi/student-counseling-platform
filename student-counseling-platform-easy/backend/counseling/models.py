from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class TimeStampedModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: abstract=True

class Student(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE='ACTIVE','فعال'; INACTIVE='INACTIVE','غیرفعال'; ARCHIVED='ARCHIVED','بایگانی‌شده'
    advisor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='students',limit_choices_to={'role':'ADVISOR'},db_index=True)
    first_name=models.CharField(max_length=80); last_name=models.CharField(max_length=80)
    student_code=models.CharField(max_length=50,unique=True,db_index=True)
    phone=models.CharField(max_length=30,blank=True); school=models.CharField(max_length=150,blank=True); grade_year=models.CharField(max_length=80,blank=True)
    field_major=models.CharField(max_length=120,blank=True); gender=models.CharField(max_length=30,blank=True); date_of_birth=models.DateField(null=True,blank=True)
    enrollment_date=models.DateField(); status=models.CharField(max_length=20,choices=Status.choices,default=Status.ACTIVE,db_index=True); notes=models.TextField(blank=True)
    def __str__(self): return f'{self.first_name} {self.last_name} ({self.student_code})'

class WeeklyPerformance(TimeStampedModel):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='weekly_performances')
    week_start=models.DateField(db_index=True)
    total_study_hours=models.DecimalField(max_digits=6,decimal_places=2,validators=[MinValueValidator(0)])
    test_questions=models.PositiveIntegerField(default=0); written_questions=models.PositiveIntegerField(default=0); advisor_notes=models.TextField(blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='weekly_created')
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='weekly_updated',null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','week_start'],name='uniq_student_week')]
        ordering=['-week_start']

class AssessmentResult(TimeStampedModel):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='assessment_results')
    assessment_name=models.CharField(max_length=180,db_index=True); assessment_date=models.DateField(db_index=True)
    overall_score=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    advisor_notes=models.TextField(blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='assessment_created')
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='assessment_updated',null=True,blank=True)
    class Meta: ordering=['-assessment_date','-created_at']

class AssessmentResultParameter(TimeStampedModel):
    assessment_result=models.ForeignKey(AssessmentResult,on_delete=models.CASCADE,related_name='parameters')
    parameter_name=models.CharField(max_length=160); value=models.DecimalField(max_digits=12,decimal_places=3)
    unit_label=models.CharField(max_length=40,blank=True); note=models.CharField(max_length=300,blank=True); display_order=models.PositiveIntegerField(default=0)
    class Meta: ordering=['display_order','id']

class StudentChallenge(TimeStampedModel):
    class Severity(models.TextChoices):
        LOW='LOW','کم'; MEDIUM='MEDIUM','متوسط'; HIGH='HIGH','زیاد'; CRITICAL='CRITICAL','بحرانی'
    class Status(models.TextChoices):
        OPEN='OPEN','باز'; IN_PROGRESS='IN_PROGRESS','در حال پیگیری'; RESOLVED='RESOLVED','حل‌شده'
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='challenges')
    title=models.CharField(max_length=180); category=models.CharField(max_length=120,db_index=True); description=models.TextField()
    severity=models.CharField(max_length=20,choices=Severity.choices,default=Severity.MEDIUM,db_index=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.OPEN,db_index=True)
    date_identified=models.DateField(db_index=True); resolution_notes=models.TextField(blank=True); resolved_date=models.DateField(null=True,blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='challenge_created')
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='challenge_updated',null=True,blank=True)
    class Meta: ordering=['-date_identified','-created_at']

class ProgramLogicCategory(models.Model):
    name=models.CharField(max_length=120,unique=True); is_system=models.BooleanField(default=False); is_active=models.BooleanField(default=True)
    def __str__(self): return self.name

class ProgramLogicReview(TimeStampedModel):
    class Rating(models.IntegerChoices):
        VERY_WEAK=1,'بسیار ضعیف'; WEAK=2,'ضعیف'; ACCEPTABLE=3,'قابل قبول'; GOOD=4,'خوب'; EXCELLENT=5,'عالی'
    class Severity(models.TextChoices):
        NONE='NONE','بدون ایراد'; MINOR='MINOR','جزئی'; MODERATE='MODERATE','متوسط'; MAJOR='MAJOR','جدی'
    class Status(models.TextChoices):
        ISSUE_IDENTIFIED='ISSUE_IDENTIFIED','ایراد ثبت شده'; SOLUTION_PROVIDED='SOLUTION_PROVIDED','راهکار ارائه شده'; AWAITING_IMPLEMENTATION='AWAITING_IMPLEMENTATION','در انتظار اجرا'; IMPLEMENTED='IMPLEMENTED','اجرا شده'; NOT_IMPLEMENTED='NOT_IMPLEMENTED','اجرا نشده'
    supervisor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='program_reviews_created',limit_choices_to={'role':'SUPERVISOR'})
    advisor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='program_reviews_received',limit_choices_to={'role':'ADVISOR'})
    student=models.ForeignKey(Student,on_delete=models.PROTECT,related_name='program_reviews',null=True,blank=True)
    review_date=models.DateField(db_index=True); overall_quality_rating=models.PositiveSmallIntegerField(choices=Rating.choices)
    error_severity=models.CharField(max_length=20,choices=Severity.choices,default=Severity.NONE,db_index=True)
    error_categories=models.ManyToManyField(ProgramLogicCategory,related_name='reviews',blank=True)
    problem_description=models.TextField(blank=True); incorrect_logic_location=models.TextField(blank=True); recommended_solution=models.TextField(blank=True)
    implementation_status=models.CharField(max_length=40,choices=Status.choices,default=Status.ISSUE_IDENTIFIED,db_index=True)
    advisor_implementation_notes=models.TextField(blank=True); date_implemented=models.DateField(null=True,blank=True); supervisor_follow_up_notes=models.TextField(blank=True)
    class Meta: ordering=['-review_date','-created_at']


class ProgramLogicReviewStatusHistory(models.Model):
    review=models.ForeignKey(ProgramLogicReview,on_delete=models.CASCADE,related_name='status_history')
    status=models.CharField(max_length=40,choices=ProgramLogicReview.Status.choices,db_index=True)
    changed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='program_review_status_changes')
    note=models.CharField(max_length=300,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']

class Activity(TimeStampedModel):
    class Type(models.TextChoices):
        STUDENT_ADDED='STUDENT_ADDED','دانش‌آموز افزوده شد'; WEEKLY_CREATED='WEEKLY_CREATED','عملکرد هفتگی ثبت شد'; ASSESSMENT_CREATED='ASSESSMENT_CREATED','نتیجه ارزیابی ثبت شد'; CHALLENGE_OPENED='CHALLENGE_OPENED','چالش ثبت شد'; CHALLENGE_RESOLVED='CHALLENGE_RESOLVED','چالش حل شد'; REVIEW_CREATED='REVIEW_CREATED','بررسی ناظر ثبت شد'; RECOMMENDATION_IMPLEMENTED='RECOMMENDATION_IMPLEMENTED','راهکار اجرا شد'
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='activities')
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True,related_name='activities')
    advisor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='advisor_activities')
    activity_type=models.CharField(max_length=50,choices=Type.choices,db_index=True); description=models.CharField(max_length=300)
    class Meta: ordering=['-created_at']
