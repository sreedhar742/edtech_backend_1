from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, BaseUserManager
# from myapp.models import classes
# Create your models here.

class School(models.Model):
    # classes=models.ManyToManyField(classes,blank=True, null=True)
    classes=models.ManyToManyField('myapp.classes')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class StudentManager(BaseUserManager):
    def create_user(self,fullname,email,roll_number,phone_number, username, password=None, **extra_fields):
        """
        Create and save a Student with the given roll number and password.
        """
        if not username:
            raise ValueError('Students must have a username')
        student = self.model(
            fullname=fullname,
            roll_number=roll_number,
            phone_number=phone_number,
            username=username, 
            email=email,
            **extra_fields)

        # Set the password (this will hash it)
        student.set_password(password)
        student.save(using=self._db)
        return student
    def create_superuser(self, username, password=None, **extra_fields):
            """
            Create and save a superuser with the given username and password.
            """
            # Provide default values for the required fields
            fullname = extra_fields.get('fullname', 'Admin')
            phone_number = extra_fields.get('phone_number', '0000000000')
            roll_number = extra_fields.get('roll_number', 'ADMIN')
            email = extra_fields.get('email')

            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)
            extra_fields.setdefault('is_student', False)
            extra_fields.setdefault('is_teacher', False)
            # Use the create_user method to create the superuser
            account = self.create_user(fullname,email, roll_number, phone_number, username, password, **extra_fields)
            account.save(using=self._db)
            return account
    

class Student(AbstractBaseUser):
    fullname = models.CharField(max_length=50, blank=True, null=True)
    roll_number = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    username = models.CharField(max_length=100,unique=True, blank=True, null= True)
    email = models.EmailField(blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    # class_name = models.ForeignKey(classes', on_delete=models.CASCADE, blank=True, null=True)
    class_name = models.ForeignKey('myapp.classes', on_delete=models.CASCADE, blank=True, null=True)
    
    # Required fields for custom user model
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)

    # Use the custom StudentManager
    objects = StudentManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Can add email or other fields if required
    
    def __str__(self):
        return str(self.roll_number)+" "+str(self.username)
    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True


# models.py
from django.db import models
from django.contrib.auth.models import User

class SessionSnapshot(models.Model):
    user = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    session_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user)+" "+str(self.timestamp)