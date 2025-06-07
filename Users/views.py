from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
# from .serializers import StudentTokenObtainPairSerializer, SubjectSerializer, SchoolClassSerializer, createChapterSerializer, ChapterSerializer, InputSerializer, TopicSerializer
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from django.db import IntegrityError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from Users.models import  School, Student
from myapp.models import classes
from rest_framework.authtoken import views as v1
from rest_framework.authtoken.models import Token

from django.db import transaction
import json
# Create your views here.

@api_view(['POST'])
@csrf_exempt
def upload_student_list(request):
        
    try:
        if request.method == 'POST':
            with transaction.atomic():
                
                if 'student_list' in request.FILES:
                    file = request.FILES['student_list']
                    df = pd.read_csv(file)

                    school_name = request.POST.get('School_Name')
                    school_code = request.POST.get('School_Code')
                    # print(School.objects.get(name=school_name, code=school_code),"========---------data-----======")
                    # Retrieve or create the school
                    
                    # Iterate over DataFrame rows
                    for _, row in df.iterrows():
                        student_name = row['Student_Name']
                        roll_number = row['Roll_Number']
                        contact = row['Contact']
                        class_name = row['Class']
                        try:
                            all_classes = classes.objects.filter()
                        except:
                            return Response({'status':"failed","description":"classes matching query does't exist"})
                       
                        school, created = School.objects.get_or_create(name=school_name, code=school_code)
                        school.classes.set(all_classes)
                        print(school)  
                        try:
                            class_obj = classes.objects.get(class_name=class_name)
                        except classes.DoesNotExist:
                            class_obj = None   
                        print(class_obj)            
                        if class_obj:
                            student_exists = Student.objects.filter(roll_number=roll_number, school=school, class_name=class_obj ).exists()
                        else:
                            student_exists = False 
                        email=str(class_name) + str(school_code) + str(roll_number) + "@gmail.com"
                        
                        if not student_exists:
                            
                            Student.objects.create_user(
                                fullname=student_name,
                                roll_number=roll_number,
                                phone_number=contact,
                                username=f"{class_name}{school_code}{roll_number}",
                                password=f"{roll_number}{school_code}",
                                email = email,
                                school=school,
                                class_name=class_obj
                            )
                            try:
                                
                                acc=Student.objects.get(email=email)
                                user_token=Token.objects.create(user=acc)
                                print(user_token)
                            except:
                                return Response({"status":"failed","description":"Email address not valid"})
                        else:
                            print(f"Student with roll number {roll_number} already exists in the school.")
                
                    return Response({"status": "Students Registered Successfully from file"})

    except IntegrityError as e:
        return Response({"status": "failed", "error": str(e)}, status=400)
    except Exception as e:
        return Response({"status": "failed", "error": str(e)}, status=400)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.middleware.csrf import get_token

@api_view(['POST'])
# Remove the csrf_exempt decorator
@permission_classes([AllowAny])
def logins(request):
    try:
        data = request.data
        # print(data)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            
            # Get all sessions linked to this user
            # user_sessions = []
            # all_sessions = Session.objects.filter(expire_date__gte=timezone.now())

            # for session in all_sessions:
            #     session_data = session.get_decoded()
            #     if str(session_data.get('_auth_user_id')) == str(user.id):
            #         user_sessions.append(session)

            # # If more than 2 sessions, delete the oldest
            # if len(user_sessions) >= 2:
            #     oldest_session = sorted(user_sessions, key=lambda s: s.expire_date)[0]
            #     oldest_session.delete()
            #     print(f"Deleted oldest session for user {user.username}")

            # Get or create token
            token, created = Token.objects.get_or_create(user=user)

            # Build response with token and session info
            response = Response({
                "status": "Success",
                "token": token.key,
                "session_key": request.session.session_key,
                "role": "teacher" if user.is_teacher else "student" if user.is_student else "admin"

            }, status=status.HTTP_200_OK)

            # Set token and sessionid cookies
            max_age = 60 * 60 * 24 * 365  # 1 year
            response.set_cookie('token', token.key, max_age=max_age, httponly=True, secure=False, samesite='Lax')
            response.set_cookie('sessionid', request.session.session_key, max_age=max_age, httponly=True, secure=False, samesite='Lax')
            
            # Set a fresh CSRF token in the cookie
            csrf_token = get_token(request)
            response.set_cookie('csrftoken', csrf_token, max_age=max_age, secure=False, samesite='Lax')

            return response

        else:
            return Response({
                "status": "Unauthorized",
                "description": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as exc:
        return Response({
            "status": "Exception",
            "description": str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def hello(request):
    return HttpResponse("Hello, world. You're at the polls index.")


# utils.py or inside views.py
from .models import SessionSnapshot

def backup_session_data(request):
    data = dict(request.session)
    # Optional: remove Django-internal keys
    data.pop('_auth_user_id', None)
    data.pop('_auth_user_backend', None)
    data.pop('_auth_user_hash', None)
    print("Backing up session data:", data)
    SessionSnapshot.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_data=data
    )

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})
from django.contrib.auth import logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def logout_view(request):
    try:
        # Backup session data before logout
        if request.user.username =="admin":
            print("Admin user detected, skipping session backup.")
            pass
        else:
            backup_session_data(request)

        if request.user.is_authenticated:
            logout(request)
            print("User logged out successfully")
            response = Response({"status": "Success"}, status=status.HTTP_200_OK)
            response.delete_cookie('token')
            response.delete_cookie('sessionid')
            return response

        return Response({"status": "Already logged out"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"status": "Error", "message": str(e)}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
from .models import SessionSnapshot

class SessionDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve session data for the authenticated user.
        """
        try:
            # Get the latest session snapshot for the user
            session_snapshot = SessionSnapshot.objects.filter(user=request.user).latest('timestamp')

            # Return the session data
            return Response({
                "status": "success",
                "session_data": session_snapshot.session_data
            }, status=status.HTTP_200_OK)

        except SessionSnapshot.DoesNotExist:
            return Response({
                "status": "error",
                "message": "No session data found for this user."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        

from .models import SessionSnapshot

class AllSessionDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all session data:
        - Admin gets all users' session data grouped by user ID.
        - Normal user gets only their session data.
        """
        try:
            user = request.user

            if user.username.lower() == "admin":
                all_snapshots = SessionSnapshot.objects.all().order_by('-timestamp')

                users_snapshots = {}
                for snapshot in all_snapshots:
                    uid = str(snapshot.user.username)
                    if uid=="admin":
                        continue
                    session_entry = {
                        "timestamp": snapshot.timestamp,
                        "session_data": snapshot.session_data
                    }
                    if uid not in users_snapshots:
                        users_snapshots[uid] = []
                    users_snapshots[uid].append(session_entry)
                # print(users_snapshots)
                return Response({
                    "status": "success",
                    "users_snapshots": users_snapshots
                }, status=status.HTTP_200_OK)

            else:
                user_snapshots = SessionSnapshot.objects.filter(user=user).order_by('-timestamp')

                if not user_snapshots.exists():
                    return Response({
                        "status": "error",
                        "message": "No session data found for this user."
                    }, status=status.HTTP_404_NOT_FOUND)

                sessions = [
                    {
                        "timestamp": snapshot.timestamp,
                        "session_data": snapshot.session_data
                    } for snapshot in user_snapshots
                ]

                return Response({
                    "status": "success",
                    "sessions": sessions
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from Users.permissions import IsTeacher  # Import the IsTeacher permission

class TeacherOnlyAPIView(APIView):
    permission_classes = [IsTeacher]  # Apply the IsTeacher permission

    def get(self, request):
        """
        API endpoint accessible only to teachers.
        """
        try:
            # Your logic for the teacher-only API endpoint goes here
            data = {"message": "This endpoint is accessible only to teachers."}
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TeacherUploadAPIView(APIView):
    """
    API endpoint to bulk upload teachers based on their school names.
    Expects a CSV file with columns: Teacher_Name, Phone_Number, Username, Password, School_Name, School_Code, Class_Name, Email
    """
    def post(self, request):
        try:
            if 'teacher_list' not in request.FILES:
                return Response({"status": "failed", "error": "No file uploaded with key 'teacher_list'."}, status=400)

            file = request.FILES['teacher_list']
            df = pd.read_csv(file)

            with transaction.atomic():
                for _, row in df.iterrows():
                    teacher_name = row.get('Teacher_Name')
                    phone_number = row.get('Phone_Number')
                    username = row.get('Username')
                    password = row.get('Password')
                    school_name = row.get('School_Name')
                    school_code = row.get('School_Code')
                    class_name = row.get('Class_Name')
                    email = row.get('Email')

                    # Get or create school
                    school, _ = School.objects.get_or_create(name=school_name, code=school_code)

                    # Get class object if provided
                    class_obj = None
                    if class_name:
                        try:
                            class_obj = classes.objects.get(class_name=class_name)
                        except classes.DoesNotExist:
                            class_obj = None

                    # Check if teacher already exists
                    teacher_exists = Student.objects.filter(username=username, school=school, is_teacher=True).exists()
                    if not teacher_exists:
                        Student.objects.create_user(
                            fullname=teacher_name,
                            roll_number=username,  # or use a separate field if available
                            phone_number=phone_number,
                            username=username,
                            password=password,
                            email=email,
                            school=school,
                            class_name=class_obj,
                            is_teacher=True,
                            is_student=False
                        )
                return Response({"status": "Teachers Registered Successfully from file"}, status=200)
        except Exception as e:
            return Response({"status": "failed", "error": str(e)}, status=400)
        
class AllStudentsAPIView(APIView):
         
    permission_classes=[IsTeacher]
    def get(self, request):
        """
        API endpoint to retrieve all students for the authenticated teacher.
        """
        try:
            # Assuming the teacher is authenticated and has a school associated
            if not request.user.is_authenticated or not request.user.is_teacher:
                return Response({"status": "error", "message": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

            school = request.user.school  # Get the school of the authenticated teacher
            students = Student.objects.filter(school=school, is_student=True).values(
                'fullname', 'roll_number', 'phone_number', 'username', 'email', 'class_name'
            )

            return Response({"status": "success", "students": list(students)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GapAnalysisReportApiView(APIView):
    pass   
class TeacheDashboardAPIView(APIView):
    """
    API endpoint for teacher dashboard.
    """
    permission_classes = [IsTeacher]  # Ensure only teachers can access this endpoint

    def get(self, request):
        try:
            # Logic for fetching teacher-specific data
            # For example, fetching classes, students, etc.
            data = {
                "message": "Welcome to the teacher dashboard.",
                # Add more data as needed
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)