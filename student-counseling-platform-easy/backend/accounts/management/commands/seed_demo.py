from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from accounts.models import User,SupervisorProfile,AdvisorProfile
from counseling.models import Student,WeeklyPerformance,AssessmentResult,AssessmentResultParameter,StudentChallenge,ProgramLogicCategory,ProgramLogicReview,ProgramLogicReviewStatusHistory,Activity

CATEGORIES=['توزیع ساعت مطالعه','حجم بیش از حد','حجم ناکافی','اولویت‌بندی درس‌ها','تخصیص سؤال تستی','تخصیص سؤال تشریحی','راهبرد مرور','آمادگی ارزیابی','تعادل برنامه زمانی','عدم تطابق با عملکرد دانش‌آموز','سایر']
class Command(BaseCommand):
    help='Create development seed data'
    @transaction.atomic
    def handle(self,*args,**kwargs):
        def make_user(username,email,role,first,last,password):
            u,_=User.objects.update_or_create(username=username,defaults={'email':email,'role':role,'first_name':first,'last_name':last,'is_active':True}); u.set_password(password); u.save(); return u
        admin=make_user('admin','admin@example.com','ADMIN','مدیر','سامانه','Admin123!'); admin.is_staff=True; admin.is_superuser=True; admin.save(update_fields=['is_staff','is_superuser','role'])
        s1=make_user('supervisor1','supervisor1@example.com','SUPERVISOR','مریم','ناظری','Supervisor123!'); SupervisorProfile.objects.get_or_create(user=s1)
        s2=make_user('supervisor2','supervisor2@example.com','SUPERVISOR','علی','راهنما','Supervisor123!'); SupervisorProfile.objects.get_or_create(user=s2)
        advisors=[]
        for i,(sup,name) in enumerate([(s1,'رضا مشاور'),(s1,'سارا احمدی'),(s2,'نازنین رضایی'),(s2,'امیر حسینی')],1):
            first,last=name.split(); a=make_user(f'advisor{i}',f'advisor{i}@example.com','ADVISOR',first,last,'Advisor123!'); AdvisorProfile.objects.update_or_create(user=a,defaults={'supervisor':sup}); advisors.append(a)
        cats=[ProgramLogicCategory.objects.get_or_create(name=n,defaults={'is_system':True})[0] for n in CATEGORIES]
        today=timezone.localdate(); monday=today-timedelta(days=today.weekday())
        for idx,a in enumerate(advisors):
            for j in range(1,4):
                code=f'ST-{idx+1}{j:02d}'; st,_=Student.objects.update_or_create(student_code=code,defaults={'advisor':a,'first_name':['آرین','هلیا','پارسا'][j-1],'last_name':['کریمی','محمدی','رضایی'][j-1]+str(idx+1),'school':'دبیرستان نمونه','grade_year':'یازدهم','field_major':'تجربی','enrollment_date':today-timedelta(days=120),'status':'ACTIVE'})
                for w in range(8):
                    ws=monday-timedelta(weeks=7-w)
                    WeeklyPerformance.objects.update_or_create(student=st,week_start=ws,defaults={'total_study_hours':Decimal(18+idx+j+w*1.25),'test_questions':220+25*w+10*j,'written_questions':35+5*w,'advisor_notes':'ثبت هفتگی نمونه','created_by':a,'updated_by':a})
                if not st.assessment_results.exists():
                    ar=AssessmentResult.objects.create(student=st,assessment_name='ارزیابی مهارت‌های مطالعه',assessment_date=today-timedelta(days=40),overall_score=Decimal('72.5'),advisor_notes='نتیجه از ارزیابی بیرون از سامانه وارد شده است.',created_by=a,updated_by=a)
                    AssessmentResultParameter.objects.bulk_create([AssessmentResultParameter(assessment_result=ar,parameter_name='تمرکز',value=Decimal('74'),display_order=1),AssessmentResultParameter(assessment_result=ar,parameter_name='مدیریت زمان',value=Decimal('68'),display_order=2),AssessmentResultParameter(assessment_result=ar,parameter_name='انگیزه',value=Decimal('77'),display_order=3)])
                    if j==1:
                        ar2=AssessmentResult.objects.create(student=st,assessment_name='ارزیابی مهارت‌های مطالعه',assessment_date=today-timedelta(days=8),overall_score=Decimal('78.0'),advisor_notes='ثبت دوم همان ارزیابی برای نمایش روند نمره کلی.',created_by=a,updated_by=a)
                        AssessmentResultParameter.objects.bulk_create([AssessmentResultParameter(assessment_result=ar2,parameter_name='تمرکز',value=Decimal('80'),display_order=1),AssessmentResultParameter(assessment_result=ar2,parameter_name='مدیریت زمان',value=Decimal('75'),display_order=2),AssessmentResultParameter(assessment_result=ar2,parameter_name='انگیزه',value=Decimal('79'),display_order=3)])
                Activity.objects.get_or_create(actor=a,student=st,advisor=a,activity_type='STUDENT_ADDED',description='پروفایل دانش‌آموز در داده توسعه ایجاد شد.')
                if j==1 and not st.challenges.exists():
                    StudentChallenge.objects.create(student=st,title='کاهش نظم در برنامه',category='مدیریت زمان',description='در دو هفته اخیر اجرای برنامه ناپیوسته بوده است.',severity='HIGH',status='IN_PROGRESS',date_identified=today-timedelta(days=12),created_by=a,updated_by=a)
                    Activity.objects.create(actor=a,student=st,advisor=a,activity_type='CHALLENGE_OPENED',description='چالش کاهش نظم در برنامه ثبت شد.')
                if j==1 and not st.program_reviews.exists():
                    seeded_status=['IMPLEMENTED','NOT_IMPLEMENTED','AWAITING_IMPLEMENTATION','AWAITING_IMPLEMENTATION'][idx]
                    r=ProgramLogicReview.objects.create(supervisor=a.advisor_profile.supervisor,advisor=a,student=st,review_date=today-timedelta(days=5),overall_quality_rating=3,error_severity='MODERATE',problem_description='توزیع ساعت مطالعه بین درس‌ها متوازن نیست.',incorrect_logic_location='برنامه هفتگی و توزیع روزانه ساعت‌ها',recommended_solution='ساعت درس‌های اولویت‌دار را در چند نوبت کوتاه‌تر توزیع کنید.',implementation_status=seeded_status,advisor_implementation_notes='راهکار طبق پیشنهاد ناظر در برنامه اعمال شد.' if seeded_status=='IMPLEMENTED' else ('در بازه مقرر اجرا نشد.' if seeded_status=='NOT_IMPLEMENTED' else ''),date_implemented=today-timedelta(days=2) if seeded_status=='IMPLEMENTED' else None)
                    r.error_categories.add(cats[0],cats[3]); ProgramLogicReviewStatusHistory.objects.create(review=r,status=r.implementation_status,changed_by=a.advisor_profile.supervisor,note='وضعیت نمونه برای نمایش گردش‌کار')
                    Activity.objects.create(actor=a.advisor_profile.supervisor,student=st,advisor=a,activity_type='REVIEW_CREATED',description='بررسی منطق برنامه توسط ناظر ثبت شد.')
                    if seeded_status=='IMPLEMENTED': Activity.objects.create(actor=a,student=st,advisor=a,activity_type='RECOMMENDATION_IMPLEMENTED',description='راهکار ناظر اجرا شد.')
        self.stdout.write(self.style.SUCCESS('Seed data created. Development credentials are documented in README.md.'))
