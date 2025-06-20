from django.contrib import admin
from django.urls import path
from .views import ChapterListCreateView, ClassListView, SubjectListView, TopicListView, SubTopicListView, QuestionAPIView, AnswerSubmit, StudentSubmitAPIView, QuestionWithImageUploadView, ChatbotAPIView, QuestionImageview,SimilarQuestionsAPIView,GapAnalysisAPIView,Questionupdateview,HistoryAPIView,UserGapAnalysisDataView
from .views import UserAverageScoreAPIView,AllStudentGapAnalysisAPIView,LeaderboardApiView,StudentNotificationsView,AddHomeworkAPIView,HomeworkSubmissionAPIView,GapAnalysisReportView,WorkSheetsApiview,Questionanswerupdateview
urlpatterns = [
        # path('chapters/', ChapterListCreateView.as_view(), name='chapter-list-create'),
        path('classes/', ClassListView.as_view(), name='class-list'),
        path('subjects/', SubjectListView.as_view(), name='subject-list'),
        path('chapters/', TopicListView.as_view(), name='chapter-list'),
        # path('topics/<int:topic_id>/',SubTopicListView.as_view(), name='topic-list'),
        #=================-------------AI APIS----------==================================
        path('aiquestions/', QuestionAPIView.as_view(), name='questions-api'),
        path('anssubmit/', AnswerSubmit.as_view(), name='ai-validation'),
        # path('student-submit/', StudentSubmitAPIView.as_view(), name='student-submit'),
        path('upload-questions/', QuestionWithImageUploadView.as_view(), name='upload-questions'),
        path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
        path('question-images/', QuestionImageview.as_view(), name='question-image'),
        path('similarquestion/',SimilarQuestionsAPIView.as_view(),name="similar-questions"),
        path('gapanalysis/',GapAnalysisAPIView.as_view(),name="gap-analysis"),
        path('questionupdate/',Questionupdateview.as_view(),name="question-update"),
        path('gapanalysis/', GapAnalysisAPIView.as_view(), name='gap-analysis'),  
        path('history/', HistoryAPIView.as_view(), name='history'),  
        path('usergapanalysis/', UserGapAnalysisDataView.as_view(), name='user-gap-analysis'),
        path('average-score/', UserAverageScoreAPIView.as_view(), name='average-score'), 
        path('allstudentgapanalysis/', AllStudentGapAnalysisAPIView.as_view(), name='all-student-gap-analysis'),  
        path('leaderboard/', LeaderboardApiView.as_view(), name='leaderboard'),
        path('add-homework/', AddHomeworkAPIView.as_view(), name='add-homework'),
        path('studentnotifications/', StudentNotificationsView.as_view(), name='student_notifications'),
        path('homework-submission/', HomeworkSubmissionAPIView.as_view(), name='homework-submission'),
        path('gap-analysis-report/', GapAnalysisReportView.as_view(), name='gap-analysis-report'),
        path('worksheets/', WorkSheetsApiview.as_view(), name='worksheets'),
        path('question-answer/', Questionanswerupdateview.as_view(), name='question-answer-update'),
]