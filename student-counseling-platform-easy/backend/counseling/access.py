from .models import Student

def students_for(user):
    qs=Student.objects.select_related('advisor','advisor__advisor_profile__supervisor')
    if user.role=='ADMIN': return qs
    if user.role=='SUPERVISOR': return qs.filter(advisor__advisor_profile__supervisor=user)
    if user.role=='ADVISOR': return qs.filter(advisor=user)
    return qs.none()

def advisors_for(user):
    from accounts.models import User
    qs=User.objects.filter(role='ADVISOR',is_active=True)
    if user.role=='ADMIN': return qs
    if user.role=='SUPERVISOR': return qs.filter(advisor_profile__supervisor=user)
    if user.role=='ADVISOR': return qs.filter(pk=user.pk)
    return qs.none()
