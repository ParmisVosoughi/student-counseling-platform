import secrets, string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserWriteSerializer, PasswordResetSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all().order_by('-date_joined')
    filterset_fields=[]
    def get_queryset(self):
        u=self.request.user; qs=User.objects.all().order_by('-date_joined')
        role=self.request.query_params.get('role'); q=self.request.query_params.get('search')
        if u.role=='ADMIN': pass
        elif u.role=='SUPERVISOR': qs=qs.filter(id__in=list(u.supervised_advisors.values_list('user_id',flat=True))+[u.id])
        else: qs=qs.filter(pk=u.pk)
        if role: qs=qs.filter(role=role)
        if q: qs=qs.filter(username__icontains=q) | qs.filter(email__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q)
        return qs.distinct()
    def get_serializer_class(self): return UserWriteSerializer if self.action in ['create','update','partial_update'] else UserSerializer
    def perform_create(self,serializer):
        if self.request.user.role not in ['ADMIN','SUPERVISOR']: from rest_framework.exceptions import PermissionDenied; raise PermissionDenied('دسترسی کافی ندارید.')
        role=serializer.validated_data.get('role')
        if self.request.user.role=='SUPERVISOR' and role!='ADVISOR': from rest_framework.exceptions import PermissionDenied; raise PermissionDenied('ناظر فقط می‌تواند مشاور ایجاد کند.')
        serializer.save()
    def perform_update(self,serializer):
        obj=self.get_object()
        if self.request.user.role=='SUPERVISOR' and obj.role!='ADVISOR': from rest_framework.exceptions import PermissionDenied; raise PermissionDenied('دسترسی کافی ندارید.')
        if self.request.user.role=='ADVISOR':
            from rest_framework.exceptions import PermissionDenied
            if obj.pk!=self.request.user.pk: raise PermissionDenied('دسترسی کافی ندارید.')
            forbidden={'role','is_active','supervisor_id','advisor_supervisor'}
            if forbidden.intersection(serializer.validated_data.keys()): raise PermissionDenied('امکان تغییر نقش یا وضعیت حساب وجود ندارد.')
        serializer.save()
    def destroy(self,request,*args,**kwargs):
        obj=self.get_object()
        if obj.pk==request.user.pk: return Response({'detail':'امکان غیرفعال‌سازی حساب جاری از این مسیر وجود ندارد.'},status=400)
        if request.user.role=='ADMIN': pass
        elif request.user.role=='SUPERVISOR' and obj.role=='ADVISOR': pass
        else: return Response({'detail':'اجازه غیرفعال‌سازی این حساب را ندارید.'},status=403)
        obj.is_active=False; obj.save(update_fields=['is_active'])
        return Response(status=204)
    @action(detail=True,methods=['post'],url_path='reset-password')
    def reset_password(self,request,pk=None):
        if request.user.role!='ADMIN': return Response({'detail':'فقط مدیر مجاز است.'},status=403)
        user=self.get_object(); s=PasswordResetSerializer(data=request.data); s.is_valid(raise_exception=True)
        user.set_password(s.validated_data['new_password']); user.save(update_fields=['password']); return Response({'detail':'رمز عبور با موفقیت تغییر کرد.'})
    @action(detail=True,methods=['post'],url_path='temporary-password')
    def temporary_password(self,request,pk=None):
        if request.user.role!='ADMIN': return Response({'detail':'فقط مدیر مجاز است.'},status=403)
        user=self.get_object(); alphabet=string.ascii_letters+string.digits+'!@#'; temp=''.join(secrets.choice(alphabet) for _ in range(14))
        user.set_password(temp); user.save(update_fields=['password']); return Response({'temporary_password':temp,'detail':'رمز موقت ایجاد شد؛ آن را فقط از مسیر امن به کاربر تحویل دهید.'})
