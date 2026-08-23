from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import User, SupervisorProfile, AdvisorProfile

class UserSerializer(serializers.ModelSerializer):
    full_name=serializers.SerializerMethodField()
    supervisor_id=serializers.SerializerMethodField()
    advisor_phone=serializers.SerializerMethodField(); specialty=serializers.SerializerMethodField(); profile_notes=serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=['id','username','email','first_name','last_name','full_name','role','is_active','supervisor_id','advisor_phone','specialty','profile_notes','date_joined','updated_at']
        read_only_fields=['date_joined','updated_at']
    def get_full_name(self,obj): return obj.get_full_name() or obj.username
    def get_advisor_phone(self,obj):
        try: return obj.advisor_profile.phone
        except AdvisorProfile.DoesNotExist: return ''
    def get_specialty(self,obj):
        try: return obj.advisor_profile.specialty
        except AdvisorProfile.DoesNotExist: return ''
    def get_profile_notes(self,obj):
        try: return obj.advisor_profile.notes
        except AdvisorProfile.DoesNotExist: return ''
    def get_supervisor_id(self,obj):
        try: return obj.advisor_profile.supervisor_id if obj.role==User.Role.ADVISOR else None
        except AdvisorProfile.DoesNotExist: return None

class UserWriteSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=False,allow_blank=False,validators=[validate_password])
    supervisor_id=serializers.PrimaryKeyRelatedField(source='advisor_supervisor',queryset=User.objects.filter(role=User.Role.SUPERVISOR,is_active=True),write_only=True,required=False)
    advisor_phone=serializers.CharField(write_only=True,required=False,allow_blank=True)
    specialty=serializers.CharField(write_only=True,required=False,allow_blank=True)
    profile_notes=serializers.CharField(write_only=True,required=False,allow_blank=True)
    class Meta:
        model=User
        fields=['id','username','email','first_name','last_name','role','is_active','password','supervisor_id','advisor_phone','specialty','profile_notes']
        read_only_fields=['id']
    def validate(self,attrs):
        request=self.context.get('request')
        if self.instance is None and 'role' not in attrs: attrs['role']=User.Role.ADVISOR
        if request and request.user.is_authenticated and request.user.role=='SUPERVISOR':
            requested_role=attrs.get('role', getattr(self.instance,'role',User.Role.ADVISOR))
            if requested_role!=User.Role.ADVISOR:
                raise serializers.ValidationError({'role':'ناظر فقط می‌تواند حساب مشاور را مدیریت کند.'})
        if request and request.user.is_authenticated and request.user.role=='ADVISOR':
            requested_role=attrs.get('role', getattr(self.instance,'role',User.Role.ADVISOR))
            if requested_role!=User.Role.ADVISOR:
                raise serializers.ValidationError({'role':'امکان تغییر نقش وجود ندارد.'})
        if self.instance is None and not attrs.get('password'): raise serializers.ValidationError({'password':'رمز عبور الزامی است.'})
        role=attrs.get('role', getattr(self.instance,'role',User.Role.ADVISOR))
        if self.instance and role!=self.instance.role:
            if self.instance.role==User.Role.ADVISOR and self.instance.students.exists():
                raise serializers.ValidationError({'role':'تا زمانی که این مشاور دانش‌آموز دارد، تغییر نقش مجاز نیست.'})
            if self.instance.role==User.Role.SUPERVISOR and self.instance.supervised_advisors.exists():
                raise serializers.ValidationError({'role':'تا زمانی که این ناظر مشاور زیرمجموعه دارد، تغییر نقش مجاز نیست.'})
        supervisor=attrs.pop('advisor_supervisor',None)
        if role==User.Role.ADVISOR:
            if request and request.user.role==User.Role.SUPERVISOR: supervisor=request.user
            elif self.instance and supervisor is None:
                try: supervisor=self.instance.advisor_profile.supervisor
                except AdvisorProfile.DoesNotExist: pass
            if supervisor is None: raise serializers.ValidationError({'supervisor_id':'برای مشاور باید ناظر مشخص شود.'})
            attrs['_supervisor']=supervisor
        return attrs
    @transaction.atomic
    def create(self,validated_data):
        supervisor=validated_data.pop('_supervisor',None); password=validated_data.pop('password'); phone=validated_data.pop('advisor_phone',''); specialty=validated_data.pop('specialty',''); notes=validated_data.pop('profile_notes','')
        user=User(**validated_data); user.set_password(password); user.save()
        if user.role==User.Role.SUPERVISOR: SupervisorProfile.objects.create(user=user)
        elif user.role==User.Role.ADVISOR: AdvisorProfile.objects.create(user=user,supervisor=supervisor,phone=phone,specialty=specialty,notes=notes)
        return user
    @transaction.atomic
    def update(self,instance,validated_data):
        supervisor=validated_data.pop('_supervisor',None); password=validated_data.pop('password',None); phone=validated_data.pop('advisor_phone',None); specialty=validated_data.pop('specialty',None); notes=validated_data.pop('profile_notes',None)
        old_role=instance.role
        for k,v in validated_data.items(): setattr(instance,k,v)
        if password: instance.set_password(password)
        instance.save()
        if instance.role==User.Role.SUPERVISOR:
            SupervisorProfile.objects.get_or_create(user=instance); AdvisorProfile.objects.filter(user=instance).delete()
        elif instance.role==User.Role.ADVISOR:
            SupervisorProfile.objects.filter(user=instance).delete()
            profile,_=AdvisorProfile.objects.get_or_create(user=instance,defaults={'supervisor':supervisor})
            changed=[]
            if supervisor and profile.supervisor_id!=supervisor.id: profile.supervisor=supervisor; changed.append('supervisor')
            if phone is not None: profile.phone=phone; changed.append('phone')
            if specialty is not None: profile.specialty=specialty; changed.append('specialty')
            if notes is not None: profile.notes=notes; changed.append('notes')
            if changed: profile.save(update_fields=list(dict.fromkeys(changed)))
        elif instance.role==User.Role.ADMIN:
            AdvisorProfile.objects.filter(user=instance).delete(); SupervisorProfile.objects.filter(user=instance).delete()
        return instance

class PasswordResetSerializer(serializers.Serializer):
    new_password=serializers.CharField(write_only=True,validators=[validate_password])
