from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from Users.models import Student


# Model for School

class classes(models.Model):
    class_name=models.CharField(max_length=50, null=True, blank=True)
    class_code=models.CharField(max_length=50, null=True, blank=True,unique=True)
    
    def __str__(self) -> str:
        return str(self.class_code)


# Model for Subject

class Subject(models.Model):
    class_name=models.ForeignKey(classes, on_delete=models.CASCADE, blank=True, null=True)
    subject_name = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return str(self.subject_name)+"-"+"class"+" "+str(self.class_name.class_name)


# Model for Topics


class Topics(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic_code = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return str(self.name)+" "+str(self.subject.subject_name)+" "+str(self.subject.class_name.class_name)

# Model for SubTopic

class SubTopics(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE,  related_name='topics')

    def __str__(self):
        return str(self.name)+" "+str(self.topic.name)

# Model for Question_Answer

class Question_Answers(models.Model):
    
    user = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    question_text = models.TextField(null=True, blank=True)
    topic = models.ManyToManyField(Topics, blank=True)
    subtopic = models.ForeignKey(SubTopics, on_delete=models.CASCADE, null=True, blank=True)
    solved = models.BooleanField(default=False)
    exercise = models.BooleanField(default=False)
    externel = models.CharField(max_length=100,blank=True, null=True)
    
    #======-------if student submit the answer that image will converted in text format from AI model and stored in this field-----============
    
    answer_image = models.TextField(null=True, blank=True)
    student_answer = models.TextField(null=True, blank=True)
     
    #============----------If student will select solve or explain that answer will stored in this field---------======================
    ai_answer = models.TextField(null=True, blank=True)
    
    question_marks = models.IntegerField(null=True, blank=True)
    ai_given_marks = models.IntegerField(null=True, blank=True)
    total_marks =models.IntegerField(null=True, blank=True)
    ai_concepts = models.TextField(null=True, blank=True)
    ai_solved = models.BooleanField(default=False)   
    ai_correct = models.BooleanField(default=False)
    ai_explain = models.BooleanField(default=False)
    date = models.DateTimeField()
 

    def __str__(self):
        return str(self.user.fullname)+" "+str(self.question_text)

class StudentSubmits(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)  # Changed from ForeignKey to CharField
    image = models.TextField()
    question = models.TextField()
    student_answer = models.TextField(null=True, blank=True)
    correction_text = models.TextField(null=True, blank=True)
    mistakes = models.TextField(null=True, blank=True)
    question_marks = models.IntegerField(null=True, blank=True)
    student_marks = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    concepts_used = models.JSONField(null=True, blank=True)
    student_answer_replication = models.TextField(null=True, blank=True)
    correct_answer_breakdown = models.JSONField(null=True, blank=True)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.student} - {self.question[:30]}"

class QuestionWithImage(models.Model):
    class_code = models.CharField(max_length=50)
    subject_code = models.CharField(max_length=50)
    topic_code = models.CharField(max_length=50)
    
    question = models.TextField()
    question_image = models.TextField(null=True, blank=True)
    answer= models.TextField(null=True, blank=True)
    typed = models.TextField(null=True, blank=True)
    sub_topic_code = models.TextField(null=True, blank=True)
    level=models.TextField(null=True, blank=True)  # Added level field
    # Make field optional
    # typed=models.TextField(null=True,blank=True)
    def __str__(self):
        return f"{self.class_code} - {self.subject_code} - {self.topic_code} - {self.question[:30]}"

class Worksheet(models.Model): 
    teacher = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='worksheets'
    )
    class_code = models.CharField(max_length=50)
    subject_code = models.CharField(max_length=50)  
    topic_code = models.CharField(max_length=50)
    worksheet_name = models.CharField(max_length=255)
    question= models.TextField(null=True, blank=True)
    question_image = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.worksheet_name}"
        
 
class GapAnalysis(models.Model): 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_name = models.TextField(null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    chapter_number = models.TextField(null=True, blank=True)
    question_text = models.TextField(null=True, blank=True)
    question_image_base64 = models.TextField(null=True, blank=True)
    student_answer_base64 = models.TextField(null=True, blank=True)
    student_answer = models.TextField(null=True, blank=True)
    student_score = models.IntegerField(null=True, blank=True)
    answering_type = models.TextField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    ai_answer = models.TextField(null=True, blank=True)
    concept_answer= models.TextField(null=True, blank=True)
    student_answering_time= models.IntegerField(null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.student.fullname} - {self.class_name} - {self.subject} - Chapter {self.chapter_number}"

class Homework(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    
    # Link to teacher who created it
    teacher = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='homeworks'
    )
    # Link to class and subject
    # class_ref = models.ForeignKey(classes, on_delete=models.CASCADE, related_name='homeworks')
    # subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homeworks')
    # topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name='homeworks')
    # subtopic = models.ForeignKey(SubTopics, on_delete=models.CASCADE, related_name='homeworks', null=True, blank=True)

    due_date = models.DateTimeField(null=True, blank=True)
    date_assigned = models.DateTimeField(auto_now_add=True)
    
    # Attachments or links (optional)
    attachment = models.TextField(null=True, blank=True)
    homework_code = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-date_assigned']


class Notification(models.Model):
    sender = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='sent_notifications'
    )
    message = models.TextField()
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.sender.username} about {self.homework.title}"


class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(
        Homework,
        to_field='homework_code',  # Use the custom code
        on_delete=models.CASCADE,
        related_name='submissions'
    )    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homework_submissions')
    submission_date = models.DateTimeField(auto_now_add=True)
    submitted_file = models.TextField(null=True, blank=True)  # Base64 encoded file or link
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.fullname} - {self.homework.title} Submission"