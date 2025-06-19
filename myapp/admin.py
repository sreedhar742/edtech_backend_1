
from django.contrib import admin
from .models import classes,Subject, Topics, SubTopics, Question_Answers,QuestionWithImage,GapAnalysis,Homework,Notification,HomeworkSubmission,Worksheet
admin.site.register(classes)
admin.site.register(Subject)
admin.site.register(Topics)
admin.site.register(SubTopics)
admin.site.register(Question_Answers)
admin.site.register(QuestionWithImage)
admin.site.register(GapAnalysis)
admin.site.register(Homework)
admin.site.register(Notification)
admin.site.register(HomeworkSubmission) 
admin.site.register(Worksheet)
from django.contrib.sessions.models import Session
from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib import admin
from datetime import timedelta

class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_date', 'expire_date', 'decoded_data']
    readonly_fields = ['decoded_data']

    def created_date(self, obj):
        # Assuming session expiry is 2 weeks (default Django setting)
        # So created_date = expire_date - 14 days
        return obj.expire_date - timedelta(weeks=2)
    created_date.short_description = 'Created Date'

    def decoded_data(self, obj):
        try:
            return obj.get_decoded()
        except Exception:
            return "Could not decode"
    decoded_data.short_description = 'Session Data (decoded)'

admin.site.register(Session, SessionAdmin)
