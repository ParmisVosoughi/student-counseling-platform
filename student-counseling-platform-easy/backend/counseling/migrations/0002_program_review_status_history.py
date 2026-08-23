from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('counseling','0001_initial'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(
            name='ProgramLogicReviewStatusHistory',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('status',models.CharField(choices=[('ISSUE_IDENTIFIED','ایراد ثبت شده'),('SOLUTION_PROVIDED','راهکار ارائه شده'),('AWAITING_IMPLEMENTATION','در انتظار اجرا'),('IMPLEMENTED','اجرا شده'),('NOT_IMPLEMENTED','اجرا نشده')],db_index=True,max_length=40)),
                ('note',models.CharField(blank=True,max_length=300)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('changed_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='program_review_status_changes',to=settings.AUTH_USER_MODEL)),
                ('review',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='status_history',to='counseling.programlogicreview')),
            ],
            options={'ordering':['-created_at']},
        )
    ]
