from datetime import timedelta
from django.db import transaction
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Student, WeeklyPerformance, AssessmentResult, AssessmentResultParameter, StudentChallenge, ProgramLogicCategory, ProgramLogicReview, ProgramLogicReviewStatusHistory, Activity
from .access import students_for, advisors_for

class StudentSerializer(serializers.ModelSerializer):
    advisor_name=serializers.SerializerMethodField(); supervisor_name=serializers.SerializerMethodField()
    class Meta:
        model=Student; fields='__all__'; read_only_fields=['created_at','updated_at']; extra_kwargs={'advisor':{'required':False}}
    def get_advisor_name(self,o): return o.advisor.get_full_name() or o.advisor.username
    def get_supervisor_name(self,o):
        try: u=o.advisor.advisor_profile.supervisor; return u.get_full_name() or u.username
        except Exception: return ''
    def validate(self,attrs):
        request=self.context['request']
        advisor=attrs.get('advisor',getattr(self.instance,'advisor',None))
        if request.user.role in ['ADMIN','SUPERVISOR'] and advisor is None:
            raise serializers.ValidationError({'advisor':'انتخاب مشاور الزامی است.'})
        return attrs
    def validate_advisor(self,advisor):
        request=self.context['request']
        if request.user.role=='ADVISOR' and advisor!=request.user: raise serializers.ValidationError('امکان تخصیص دانش‌آموز به مشاور دیگر وجود ندارد.')
        if request.user.role=='SUPERVISOR' and not advisors_for(request.user).filter(pk=advisor.pk).exists(): raise serializers.ValidationError('این مشاور زیرمجموعه شما نیست.')
        return advisor

class WeeklyPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model=WeeklyPerformance; fields='__all__'; read_only_fields=['created_by','updated_by','created_at','updated_at']
    def validate_student(self,student):
        if not students_for(self.context['request'].user).filter(pk=student.pk).exists(): raise serializers.ValidationError('به این دانش‌آموز دسترسی ندارید.')
        return student
    def validate(self,attrs):
        student=attrs.get('student',getattr(self.instance,'student',None)); week=attrs.get('week_start',getattr(self.instance,'week_start',None))
        if week:
            week=week-timedelta(days=week.weekday()); attrs['week_start']=week
        q=WeeklyPerformance.objects.filter(student=student,week_start=week)
        if self.instance: q=q.exclude(pk=self.instance.pk)
        if q.exists(): raise serializers.ValidationError({'week_start':'برای این دانش‌آموز در این هفته قبلاً رکورد ثبت شده است.'})
        return attrs

class AssessmentParameterSerializer(serializers.ModelSerializer):
    class Meta: model=AssessmentResultParameter; fields=['id','parameter_name','value','unit_label','note','display_order']; read_only_fields=['id']

class AssessmentResultSerializer(serializers.ModelSerializer):
    parameters=AssessmentParameterSerializer(many=True,required=False)
    class Meta: model=AssessmentResult; fields=['id','student','assessment_name','assessment_date','overall_score','advisor_notes','parameters','created_by','updated_by','created_at','updated_at']; read_only_fields=['created_by','updated_by','created_at','updated_at']
    def validate_student(self,student):
        if not students_for(self.context['request'].user).filter(pk=student.pk).exists(): raise serializers.ValidationError('به این دانش‌آموز دسترسی ندارید.')
        return student
    @transaction.atomic
    def create(self,validated_data):
        params=validated_data.pop('parameters',[]); obj=super().create(validated_data)
        AssessmentResultParameter.objects.bulk_create([AssessmentResultParameter(assessment_result=obj,**p) for p in params]); return obj
    @transaction.atomic
    def update(self,instance,validated_data):
        params=validated_data.pop('parameters',None); obj=super().update(instance,validated_data)
        if params is not None:
            obj.parameters.all().delete(); AssessmentResultParameter.objects.bulk_create([AssessmentResultParameter(assessment_result=obj,**p) for p in params])
        return obj

class StudentChallengeSerializer(serializers.ModelSerializer):
    class Meta: model=StudentChallenge; fields='__all__'; read_only_fields=['created_by','updated_by','created_at','updated_at']
    def validate_student(self,student):
        if not students_for(self.context['request'].user).filter(pk=student.pk).exists(): raise serializers.ValidationError('به این دانش‌آموز دسترسی ندارید.')
        return student
    def validate(self,attrs):
        status=attrs.get('status',getattr(self.instance,'status',None)); resolved=attrs.get('resolved_date',getattr(self.instance,'resolved_date',None))
        if status=='RESOLVED' and not resolved: raise serializers.ValidationError({'resolved_date':'برای چالش حل‌شده تاریخ حل الزامی است.'})
        return attrs

class ProgramLogicCategorySerializer(serializers.ModelSerializer):
    class Meta: model=ProgramLogicCategory; fields='__all__'


class ProgramLogicReviewStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name=serializers.SerializerMethodField()
    class Meta:
        model=ProgramLogicReviewStatusHistory
        fields=['id','status','changed_by','changed_by_name','note','created_at']
    def get_changed_by_name(self,obj): return obj.changed_by.get_full_name() or obj.changed_by.username

class ProgramLogicReviewSerializer(serializers.ModelSerializer):
    error_category_ids=serializers.PrimaryKeyRelatedField(source='error_categories',queryset=ProgramLogicCategory.objects.filter(is_active=True),many=True,write_only=True,required=False)
    error_categories=ProgramLogicCategorySerializer(many=True,read_only=True)
    advisor_name=serializers.SerializerMethodField(); student_name=serializers.SerializerMethodField(); status_history=ProgramLogicReviewStatusHistorySerializer(many=True,read_only=True)
    class Meta:
        model=ProgramLogicReview
        fields=['id','supervisor','advisor','advisor_name','student','student_name','review_date','overall_quality_rating','error_severity','error_categories','error_category_ids','problem_description','incorrect_logic_location','recommended_solution','implementation_status','advisor_implementation_notes','date_implemented','supervisor_follow_up_notes','status_history','created_at','updated_at']
        read_only_fields=['supervisor','created_at','updated_at']
    def get_advisor_name(self,o): return o.advisor.get_full_name() or o.advisor.username
    def get_student_name(self,o): return str(o.student) if o.student else ''
    def validate(self,attrs):
        req=self.context['request']; advisor=attrs.get('advisor',getattr(self.instance,'advisor',None)); student=attrs.get('student',getattr(self.instance,'student',None))
        if req.user.role=='SUPERVISOR' and not advisors_for(req.user).filter(pk=advisor.pk).exists(): raise serializers.ValidationError({'advisor':'این مشاور زیرمجموعه شما نیست.'})
        if req.user.role=='ADVISOR' and advisor!=req.user: raise serializers.ValidationError({'advisor':'دسترسی ندارید.'})
        if student and student.advisor_id!=advisor.id: raise serializers.ValidationError({'student':'دانش‌آموز انتخاب‌شده متعلق به این مشاور نیست.'})
        status=attrs.get('implementation_status',getattr(self.instance,'implementation_status',None)); implemented=attrs.get('date_implemented',getattr(self.instance,'date_implemented',None))
        if status=='IMPLEMENTED' and not implemented: raise serializers.ValidationError({'date_implemented':'برای وضعیت اجراشده، تاریخ اجرا الزامی است.'})
        return attrs

class ActivitySerializer(serializers.ModelSerializer):
    actor_name=serializers.SerializerMethodField(); student_name=serializers.SerializerMethodField()
    class Meta: model=Activity; fields=['id','activity_type','description','actor','actor_name','student','student_name','advisor','created_at']
    def get_actor_name(self,o): return (o.actor.get_full_name() or o.actor.username) if o.actor else ''
    def get_student_name(self,o): return str(o.student) if o.student else ''
