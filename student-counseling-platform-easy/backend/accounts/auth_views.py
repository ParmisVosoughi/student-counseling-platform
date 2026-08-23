from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import UserSerializer

class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=TokenObtainPairSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        refresh=serializer.validated_data['refresh']; access=serializer.validated_data['access']
        token=RefreshToken(refresh); user_id=token['user_id']
        from .models import User
        user=User.objects.get(pk=user_id)
        response=Response({'access':access,'user':UserSerializer(user).data})
        response.set_cookie(settings.REFRESH_COOKIE_NAME,refresh,httponly=True,secure=settings.REFRESH_COOKIE_SECURE,samesite=settings.REFRESH_COOKIE_SAMESITE,max_age=7*24*3600,path='/api/auth/')
        return response

class RefreshCookieView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        raw=request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not raw: return Response({'detail':'نشست منقضی شده است.'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh=RefreshToken(raw); access=str(refresh.access_token)
            user_id=refresh['user_id']
            from .models import User
            user=User.objects.get(pk=user_id,is_active=True)
            return Response({'access':access,'user':UserSerializer(user).data})
        except (TokenError, User.DoesNotExist):
            return Response({'detail':'نشست معتبر نیست.'},status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        raw=request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if raw:
            try: RefreshToken(raw).blacklist()
            except TokenError: pass
        response=Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.REFRESH_COOKIE_NAME,path='/api/auth/')
        return response
