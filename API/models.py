from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from FaceAPI.FireBase import StorageImage
import uuid


class Menus(models.Model):
    user_type_data = ((1, "Admin"), (2, "Staff"),
                      (3, "Trainer"), (4, "Student"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Description = models.CharField(max_length=250, null=True, blank=True)
    Url = models.TextField(null=True, blank=True)
    user_type = models.CharField(
        choices=user_type_data, default=1, max_length=10)
    objects = models.Manager()

class SubMenus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Menu = models.ForeignKey(Menus, on_delete=models.CASCADE)
    Description = models.CharField(max_length=250, null=True, blank=True)
    Url = models.TextField(null=True, blank=True)
    objects = models.Manager()

class Faculties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    Descriptions = models.CharField(max_length=255, null=True, blank=True)
    objects = models.Manager()

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_type_data = ((1, "Admin"), (2, "Staff"),
                      (3, "Trainer"), (4, "Student"))
    user_type = models.CharField(
        choices=user_type_data, default=1, max_length=10)
    telephone = models.CharField(
        max_length=15, null=True, blank=True, unique=True)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    faculty = models.ForeignKey(
        Faculties, on_delete=models.SET_NULL, null=True, blank=True)
    Avatar = models.TextField(default=StorageImage.GetImageDefaultAvatar(), null=True, blank=True)
    code = models.CharField(max_length=6, null=True, blank=True)


class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    objects = models.Manager()


class Staffs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    objects = models.Manager()

class Classes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Name = models.CharField(max_length=255, unique=True)
    StartDate = models.DateField(default=timezone.now, null=True, blank=True)
    IsActive = models.BooleanField(default=1)
    faculty = models.ForeignKey(
        Faculties, on_delete=models.SET_NULL, null=True, blank=True)
    objects = models.Manager()



class Students(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    PersonId = models.UUIDField()
    Class = models.ForeignKey(
        Classes, on_delete=models.SET_NULL, null=True, blank=True)
    Staff = models.UUIDField()
    objects = models.Manager()



class ImageStudent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)
    FaceId = models.CharField(max_length=250, null=True, blank=True)
    Url = models.TextField(null=True, blank=True)
    objects = models.Manager()


class Trainers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    Staff = models.UUIDField()
    objects = models.Manager()


class Courses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    Code = models.CharField(max_length=250, null=True, blank=True, unique=True)
    Descriptions = models.CharField(max_length=255, null=True, blank=True)
    IsActive = models.BooleanField(default=True, null=True, blank=True)
    faculty = models.ForeignKey(
        Faculties, on_delete=models.SET_NULL, null=True, blank=True)
    objects = models.Manager()


class Lessons(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    Name = models.CharField(max_length=255, null=True, blank=True)
    Session = models.IntegerField(null=True, blank=True)
    objects = models.Manager()


class ClassCourse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Class = models.ForeignKey(Classes, on_delete=models.CASCADE)
    Course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    Trainer = models.ForeignKey(
        Trainers, on_delete=models.SET_NULL, null=True, blank=True)
    IsActive = models.BooleanField(default=1)
    objects = models.Manager()


class StatusAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Status = models.CharField(max_length=250, null=True, blank=True)
    objects = models.Manager()


class ClassRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Name = models.CharField(max_length=250, null=True, blank=True)
    objects = models.Manager()


class Slots(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Slot = models.CharField(max_length=250, null=True, blank=True)
    StartTime = models.TimeField(default=None, null=True, blank=True)
    EndTime = models.TimeField(default=None, null=True, blank=True)
    objects = models.Manager()


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    Lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)
    Date = models.DateField(null=True, blank=True)
    Slot = models.ForeignKey(
        Slots, on_delete=models.SET_NULL, null=True, blank=True)
    Status = models.ForeignKey(
        StatusAttendance, on_delete=models.CASCADE, default="9042b79c791c4a7e993460704fddbe53")
    ClassRoom = models.ForeignKey(
        ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    ClassCourse = models.ForeignKey(ClassCourse, on_delete=models.CASCADE)
    objects = models.Manager()
