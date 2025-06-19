# Users/urls.py - Update your existing URLs with these new endpoints

from django.contrib import admin
from django.urls import path
from Users.views import upload_student_list, logins, hello, get_csrf_token, logout_view, SessionDataView, AllSessionDataView
from Users.views import TeacherOnlyAPIView, AllStudentsAPIView, TeacherUploadAPIView
from Users.views import TeacherDashboardAPIView, StudentDetailAPIView, ConceptAnalysisAPIView, GapAnalysisStatsAPIView

urlpatterns = [
    # Your existing URLs...
    path("upload/", upload_student_list, name='registered-students-api'),
    path("login/", logins, name='login'),    
    path('hello/', hello, name='hello'),
    path('csrf/', get_csrf_token),
    path('logout/', logout_view, name='logout'),
    path('sessiondata/', SessionDataView.as_view(), name='session-data'),
    path('allsessionsdata/', AllSessionDataView.as_view(), name='all-session-data'),
    path('teacher/', TeacherOnlyAPIView.as_view(), name='teacher-only'),
    path('teacherupload/', TeacherUploadAPIView.as_view(), name='teacher-upload'),
    path('allstudents/', AllStudentsAPIView.as_view(), name='all-students'),
    
    # New Mathematics Gap Analysis Dashboard URLs
    path('teacher-dashboard/', TeacherDashboardAPIView.as_view(), name='teacher_dashboard'),
    path('student-detail/<str:student_username>/', StudentDetailAPIView.as_view(), name='student_detail'),
    path('concept-analysis/<str:student_username>/<str:chapter_name>/', ConceptAnalysisAPIView.as_view(), name='concept_analysis'),
    path('gap-analysis-stats/', GapAnalysisStatsAPIView.as_view(), name='gap_analysis_stats'),
]