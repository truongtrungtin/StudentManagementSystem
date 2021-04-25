from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import register
from django.views import View
from django.contrib import messages
from API.models import (CustomUser, Staffs, Students, ImageStudent,
                        Trainers, Classes, Courses, Lessons, ClassCourse,
                        StatusAttendance, Attendance, Faculties, ClassRoom, Slots)
from App.Define import (paginators, GetStudent, GetCustomUser, RandomPassword,
                        GetUsernameFromFullnameStudent, GetTrainer, GetCodeForCourse,
                        GetUsernameFromFullnameTrainer, GetClass, CoursesNoneClass,
                        GetCourses, CreateAttendaces, RemoveAttendanceWithStudent,
                        RemoveStudentInClass, CreateAttendacesWithStudents, RemoveAttendanceWithCourse,
                        RemoveCoursesInClass, CreateAttendacesWithCourse, SendMailChangePassword,
                        SendMailCreateAccount, UpdateAttendance
                        )
from App.forms import (StudentStatus, UserUpdateForm, ImageStudent, CourseStatus,
                       UploadAvatar, UserCreateForm, CourseForm, FacultyForm, SlotsForm,
                       TrainerStatus, ClassesForm, AddStudentForm, AddCoursesForm, AddTrainerToClass,
                       AttendanceForm, ChangePassword, UploadClassesForm, ScheduleForm, ScheduleForCourseForm)
from FaceAPI import FaceAPI
from FaceAPI.FireBase import StorageImage

import time
from datetime import datetime
from App.Scheduling import Population, Schedule, GeneticAlgorithm

@register.filter
def GetImage(value):
    return StorageImage.GetImage(value)

class StaffPage(View):
    def get(self, request):
        context = {
            'total_students': Students.objects.filter(admin__faculty=request.user.faculty),
            'total_trainers': Trainers.objects.filter(admin__faculty=request.user.faculty),
            'total_courses': Courses.objects.filter(faculty=request.user.faculty),
            'total_classes': Classes.objects.filter(faculty=request.user.faculty),
        }
        return render(request, "StaffPage/index.html", context=context)


class ListViewAccountStudents(View):
    def get(self, request):
        context = {
            'students': paginators(request, Students.objects.filter(admin__faculty=request.user.faculty))
        }
        return render(request, "StaffPage/Students/ListView.html", context=context)

    def post(self, request):
        form = StudentStatus(request.POST or None, instance=GetCustomUser(
            request.POST.get('username')))
        if form.is_valid():
            form.save()
            if request.POST.get('Status') == 'Lock':
                messages.success(
                    request, f'Locked {request.POST.get("username")} account successfully.')
            else:
                messages.success(
                    request, f'UnLocked {request.POST.get("username")} account successfully.')
        else:
            if request.POST.get('Status') == 'Lock':
                messages.warning(
                    request, f'Failed to lock  {request.POST.get("username")} account successfully.')
            else:
                messages.warning(
                    request, f'Failed to unLock {request.POST.get("username")} account successfully.')
        return redirect(f'ListViewAccountStudents')

# Create student account


class CreateAccountStudent(View):
    def get(self, request):
        context = {
            # 'faculties': Faculties.objects.all(),
        }
        return render(request, "StaffPage/Students/Create.html", context=context)

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists():
                messages.warning(request, f'Email already exists!')
                return redirect('ListViewAccountStudents')
            if CustomUser.objects.filter(telephone=form.cleaned_data["telephone"].replace(" ", "")).exists():
                messages.warning(request, f'Telephone already exists!')
                return redirect('ListViewAccountStudents')
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            fullname = first_name + " " + last_name
            username = GetUsernameFromFullnameStudent(request, fullname)
            password = RandomPassword(8)
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            telephone = form.cleaned_data["telephone"].replace(" ", "")
            birthday = form.cleaned_data["birthday"]
            faculty = request.user.faculty.id
            person_id = FaceAPI.SubmitStudent(username)
            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      last_name=last_name, first_name=first_name, address=address,
                                                      telephone=telephone, birthday=birthday, faculty_id=faculty, user_type=4)
                student = Students.objects.create(
                    admin_id=user.id, PersonId=person_id, Staff=request.user.id)
                if request.FILES.get('Avatar') is not None:
                    avatar = UploadAvatar(
                        request.FILES, instance=GetCustomUser(username))
                    avatar = avatar.save(commit=False)
                    avatar.Avatar = StorageImage.SaveImage(id=GetCustomUser(username).id,
                                                               image=request.FILES.get('Avatar'),
                                                               url=f'Avatar/{GetCustomUser(username).user_type}')
                    avatar.save()
                SendMailCreateAccount(email, username, password)
                messages.success(request,
                                 f'Create Account Success. Account and password have been sent to the registration email.')
                return redirect('DetailAccountStudent', username)
            except:
                user = CustomUser.objects.filter(username=username)
                if user.exists():
                    CustomUser.delete(
                        CustomUser.objects.get(username=username))
                    FaceAPI.DeleteStudent(person_id)
                if Students.objects.filter(admin_id=user).exists():
                    Students.delete(Students.objects.get(admin_id=user))
                messages.warning(request, f'Student account creation failed!')
                return redirect('ListViewAccountStudents')
        else:
            messages.warning(request, f'Student account creation failed!')
        return redirect('ListViewAccountStudents')

# Update profile Student


class UpdateAccountStudent(View):
    def get(self, request, Username):
        context = {
            'student': GetStudent(Username),
            # 'images': ImageStudent.objects.filter(Student=GetStudent(Username).id),
            # 'faculties': Faculties.objects.all(),
        }
        return render(request, "StaffPage/Students/Update.html", context=context)

    def post(self, request, Username):
        if request.POST.get('_Save') == 'ChangeProfile':
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists() and GetCustomUser(
                        Username).email != form.cleaned_data["email"]:
                    messages.warning(request, f'Email already exists!')
                    return redirect('ListViewAccountStudents')
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"].replace(" ", "")).exists() and GetCustomUser(
                        Username).telephone != form.cleaned_data["telephone"].replace(" ", ""):
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('ListViewAccountStudents')
                email = form.cleaned_data["email"]
                address = form.cleaned_data["address"]
                telephone = form.cleaned_data["telephone"].replace(" ", "")
                birthday = form.cleaned_data["birthday"]
                # faculty = form.cleaned_data["faculty"]
                try:
                    # save CustomUser
                    user = CustomUser.objects.get(username=Username)
                    user.email = email
                    user.address = address
                    user.telephone = telephone
                    user.birthday = birthday
                    # user.faculty_id = faculty
                    user.save()
                    student = Students.objects.get(admin_id=user.id)
                    student.save()
                    if request.FILES.get('Avatar') is not None:
                        avatar = UploadAvatar(
                            request.FILES, instance=GetCustomUser(Username))
                        avatar = avatar.save(commit=False)
                        avatar.Avatar = StorageImage.SaveImage(id=GetCustomUser(Username).id,
                                                               image=request.FILES.get('Avatar'),
                                                               url=f'Avatar/{GetCustomUser(Username).user_type}')
                        avatar.save()
                except:
                    messages.warning(
                        request, f'Profile of {Username} update failed!')
                messages.success(
                    request, f'Profile of {Username} has been updated!')
            else:
                messages.warning(
                    request, f'Profile of {Username} update failed!')
            return redirect('DetailAccountStudent', Username)

# Detail Student


class DetailAccountStudent(View):
    def get(self, request, Username):
        context = {
            'student': GetStudent(Username),
            'images': ImageStudent.objects.filter(Student=GetStudent(Username).id),
            # 'faculties': Faculties.objects.all(),
        }
        return render(request, "StaffPage/Students/Detail.html", context=context)

    def post(self, request, Username):
        if request.POST.get('_Save') == 'AddImage':
            listimage = []
            for i in request.FILES.getlist('Url'):
                faceid = FaceAPI.face_client.person_group_person.add_face_from_stream(FaceAPI.PERSON_GROUP_ID,
                                                                                      Students.objects.get(
                                                                                          id=GetStudent(
                                                                                              Username).id).PersonId, i)
                image = ImageStudent(Student_id=GetStudent(Username).id,
                                     Url=StorageImage.SaveImage(id=GetStudent(Username).id, image=i, url="ImageStudent"),
                                     FaceId=faceid.persisted_face_id)
                listimage.append(image)
                if len(request.FILES.getlist('Url')) > 20:
                    time.sleep(4)
            for img in listimage:
                img.save()
            if len(request.FILES.getlist("Url")) == 1:
                messages.success(
                    request, f'Upload {len(request.FILES.getlist("Url"))} image success!')
            else:
                messages.success(
                    request, f'Upload {len(request.FILES.getlist("Url"))} images success!')
            FaceAPI.TrainPersonGroup()
            try:
                pass
            except:
                messages.warning(request, f'Upload images faild!')
            return redirect('DetailAccountStudent', Username)
        elif request.POST.get('_DeleteImage') == 'DeleteImage':
            try:
                img = ImageStudent.objects.get(id=request.POST.get('id'))
                FaceAPI.DeleteImage(img.Url, Students.objects.get(id=img.Student.id).PersonId, img.FaceId)
                img.delete()
                FaceAPI.TrainPersonGroup()
                messages.success(request, f'Delete images success!')
            except:
                messages.warning(request, f'Delete images unsuccess!')
            return redirect('DetailAccountStudent', Username)
        elif request.POST.get('_Status') != None:
            form = StudentStatus(request.POST or None, instance=GetCustomUser(
                request.POST.get('username')))
            if form.is_valid():
                form.save()
                if request.POST.get('Status') == 'Lock':
                    messages.success(
                        request, f'Locked {request.POST.get("username")} account successfully.')
                else:
                    messages.success(
                        request, f'UnLocked {request.POST.get("username")} account successfully.')
            else:
                if request.POST.get('Status') == 'Lock':
                    messages.warning(
                        request, f'Failed to lock  {request.POST.get("username")} account successfully.')
                else:
                    messages.warning(
                        request, f'Failed to unLock {request.POST.get("username")} account successfully.')
            return redirect('DetailAccountStudent', Username)

# list trainer


class ListViewAccountTrainers(View):
    def get(self, request):
        context = {
            'trainers': paginators(request, Trainers.objects.filter(admin__user_type=3, admin__faculty__id=request.user.faculty.id))
        }
        return render(request, "StaffPage/Trainers/ListView.html", context=context)

    def post(self, request):
        form = TrainerStatus(request.POST or None, instance=GetCustomUser(
            request.POST.get('username')))
        if form.is_valid():
            form.save()
            if request.POST.get('Status') == 'Lock':
                messages.success(
                    request, f'Locked {request.POST.get("username")} account successfully.')
            else:
                messages.success(
                    request, f'UnLocked {request.POST.get("username")} account successfully.')
        else:
            if request.POST.get('Status') == 'Lock':
                messages.warning(
                    request, f'Failed to lock  {request.POST.get("username")} account successfully.')
            else:
                messages.warning(
                    request, f'Failed to unLock {request.POST.get("username")} account successfully.')
        return redirect('ListViewAccountTrainers')
# Create trainer


class CreateAccountTrainer(View):
    def get(self, request):
        return render(request, "StaffPage/Trainers/Create.html")

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists():
                messages.warning(request, f'Email already exists!')
                return redirect('ListViewAccountTrainers')
            if CustomUser.objects.filter(telephone=form.cleaned_data["telephone"]).exists():
                messages.warning(request, f'Telephone already exists!')
                return redirect('ListViewAccountTrainers')
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            fullname = first_name + " " + last_name
            username = GetUsernameFromFullnameTrainer(request, fullname)
            password = RandomPassword(8)
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            telephone = form.cleaned_data["telephone"].replace(" ", "")
            birthday = form.cleaned_data["birthday"]
            faculty = request.user.faculty.id
            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      last_name=last_name, first_name=first_name, address=address,
                                                      telephone=telephone, birthday=birthday, faculty_id=faculty, user_type=3)

                trainer = Trainers.objects.create(
                    admin_id=user.id, Staff=request.user.id)
                if request.FILES.get('Avatar') is not None:
                    avatar = UploadAvatar(
                        request.FILES, instance=GetCustomUser(username))
                    avatar = avatar.save(commit=False)
                    avatar.Avatar = StorageImage.SaveImage(id=GetCustomUser(username).id,
                                                           image=request.FILES.get('Avatar'),
                                                           url=f'Avatar/{GetCustomUser(username).user_type}/')
                    avatar.save()
                SendMailCreateAccount(email, username, password)
                messages.success(request,
                                 f'Create Account Success. Account and password have been sent to the registration email.')
                return redirect('DetailAccountTrainer', username)
            except:
                user = CustomUser.objects.filter(username=username)
                if user.exists():
                    CustomUser.delete(
                        CustomUser.objects.get(username=username))
                if Trainers.objects.get(admin_id=user.id).exists():
                    Trainers.delete(Trainers.objects.get(admin_id=user.id))
                messages.warning(request, f'Trainer account creation failed')
                redirect('ListViewAccountTrainers')
        else:
            messages.warning(request, f'Trainer account creation failed')
        redirect('ListViewAccountTrainers')

# Update trainer


class UpdateAccountTrainer(View):
    def get(self, request, Username):
        context = {
            'trainer': GetTrainer(Username)
        }
        return render(request, "StaffPage/Trainers/Update.html", context=context)

    def post(self, request, Username):
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists() and GetCustomUser(Username).email != \
                    form.cleaned_data["email"]:
                messages.warning(request, f'Email already exists!')
                return redirect('DetailAccountTrainer', Username)
            if CustomUser.objects.filter(
                    telephone=form.cleaned_data["telephone"].replace(" ", "")).exists() and GetCustomUser(
                    Username).telephone != form.cleaned_data["telephone"].replace(" ", ""):
                messages.warning(request, f'Telephone already exists!')
                return redirect('DetailAccountTrainer', Username)
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            telephone = form.cleaned_data["telephone"].replace(" ", "")
            birthday = form.cleaned_data["birthday"]
            faculty = form.cleaned_data["faculty"]
            try:
                # save CustomUser
                user = CustomUser.objects.get(username=Username)
                user.email = email
                user.address = address
                user.telephone = telephone
                user.birthday = birthday
                user.faculty_id = faculty
                user.save()

                if request.FILES.get('Avatar') is not None:
                    avatar = UploadAvatar(
                        request.FILES, instance=GetCustomUser(Username))
                    avatar = avatar.save(commit=False)
                    avatar.Avatar = StorageImage.SaveImage(id=GetCustomUser(Username).id,
                                                           image=request.FILES.get('Avatar'),
                                                           url=f'Avatar/{GetCustomUser(Username).user_type}/')
                    avatar.save()
            except:
                messages.warning(
                    request, f'Profile of {Username} update failed!')
            messages.success(
                request, f'Profile of {Username} has been updated!')
        else:
            messages.warning(request, f'Profile of {Username} update failed!')
        return redirect('DetailAccountTrainer', Username)

# Detail trainer


class DetailAccountTrainer(View):
    def get(self, request, Username):
        context = {
            'trainer': GetTrainer(Username),
        }
        return render(request, "StaffPage/Trainers/Detail.html", context=context)

    def post(self, request, Username):
        if request.POST.get('_Status') != None:
            form = StudentStatus(request.POST or None, instance=GetCustomUser(
                request.POST.get('username')))
            if form.is_valid():
                form.save()
                if request.POST.get('Status') == 'Lock':
                    messages.success(
                        request, f'Locked {request.POST.get("username")} account successfully.')
                else:
                    messages.success(
                        request, f'UnLocked {request.POST.get("username")} account successfully.')
            else:
                if request.POST.get('Status') == 'Lock':
                    messages.warning(
                        request, f'Failed to lock  {request.POST.get("username")} account successfully.')
                else:
                    messages.warning(
                        request, f'Failed to unLock {request.POST.get("username")} account successfully.')
            return redirect('DetailAccountTrainer', Username)


# Course
class ListViewCourse(View):
    def get(self, request):
        context = {
            'courses': paginators(request, Courses.objects.filter(faculty=request.user.faculty))
        }
        return render(request, "StaffPage/Course/ListView.html", context=context)

    def post(self, request):
        form = CourseStatus(request.POST or None,
                            instance=GetCourses(request.POST.get('id')))
        if form.is_valid():
            form.save()
            if request.POST.get('Status') == 'Lock':
                messages.success(
                    request, f'Locked {request.POST.get("Username")} account successfully.')
            else:
                messages.success(
                    request, f'UnLocked {request.POST.get("Username")} account successfully.')
        else:
            if request.POST.get('Status') == 'Lock':
                messages.warning(
                    request, f'Failed to lock  {request.POST.get("Username")} account successfully.')
            else:
                messages.warning(
                    request, f'Failed to unLock {request.POST.get("Username")} account successfully.')
        return redirect('ListViewCourse')


class CreateCourse(View):
    def get(self, request):
        context = {
            # 'faculties': Faculties.objects.all(),
        }
        return render(request, "StaffPage/Course/Create.html", context=context)

    def post(self, request):
        form = CourseForm(request.POST or None)
        # Code = GetCodeForCourse(request.POST.get("Name"))
        Code = request.POST.get("Name")
        if form.is_valid():
            form = form.save(commit=False)
            form.Code = Code
            form.save()
            messages.success(
                request, f'Create course {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Create course {request.POST.get("Name")} unsuccessful!')
        if int(request.POST.get("Lessons")) > 0:
            lessons = []
            for i in range(1, int(request.POST.get("Lessons")) + 1):
                lesson = Lessons(Course=Courses.objects.get(
                    Code=Code), Name="Lesson {}".format(i), Session=i)
                lessons.append(lesson)
            for item in lessons:
                item.save()
        return redirect('ListViewCourse')


class UpdateCourse(View):
    form = CourseForm()

    def get(self, request, id):
        context = {
            'course': get_object_or_404(Courses, id=id),
            'faculties': Faculties.objects.all(),
        }
        return render(request, "StaffPage/Course/Update.html", context=context)

    def post(self, request, id):
        form = CourseForm(request.POST or None, instance=GetCourses(id))
        if form.is_valid():
            form = form.save(commit=False)
            form.Code = form.cleaned_data['Code']
            form.save()
            messages.success(
                request, f'Update course {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Update course {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewCourse')


class DetailCourse(View):
    def get(self, request, id):
        context = {
            'course': get_object_or_404(Courses, id=id),
            'lessons': paginators(request, get_object_or_404(Courses, id=id).lessons_set.all()),
        }
        return render(request, "StaffPage/Course/Detail.html", context=context)


# Classes
class ListViewClass(View):
    @register.filter
    def get_courses(self, isActive):
        return self.filter(IsActive=isActive)

    def get(self, request):
        context = {
            'class': paginators(request, Classes.objects.filter(faculty=request.user.faculty))
        }
        return render(request, "StaffPage/Classes/ListView.html", context=context)


class CreateClass(View):

    def get(self, request):
        context = {
            'classes': Classes.objects.filter(faculty=request.user.faculty),
            'studentsNoneClass': Students.objects.filter(Class=None, admin__faculty=request.user.faculty),
            'courses': Courses.objects.filter(faculty=request.user.faculty)
        }
        return render(request, "StaffPage/Classes/Create.html", context=context)

    def post(self, request):
        form = ClassesForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.faculty = request.user.faculty
            form.save()
            messages.success(
                request, f'Create class {request.POST.get("Name")} successful!')
            list_students_success = []
            list_courses_success = []
            if len(request.POST.getlist('Username')) > 0:
                list_fail = []
                for i in request.POST.getlist('Username'):
                    form_s = AddStudentForm(request.POST or None,
                                            instance=get_object_or_404(Students, admin__username=i))
                    if form_s.is_valid():
                        form_s = form_s.save(commit=False)
                        form_s.Class = GetClass(request.POST.get("Name"))
                        form_s.save()
                        list_students_success.append(i)
                    else:
                        list_fail.append(i)
                if len(list_students_success) > 0:
                    messages.success(request, f'List of students added to {request.POST.get("Name")}'
                                              f' class: {list_students_success}')
                if len(list_fail) > 0:
                    messages.warning(request, f'List of students unsuccessfully added to {request.POST.get("Name")}'
                                              f'class: {list_fail}')
            if len(request.POST.getlist('Courses')) > 0:
                list_fail = []
                for i in request.POST.getlist('Courses'):
                    try:
                        classcourse = ClassCourse.objects.create(Class_id=GetClass(
                            request.POST.get("Name")).id, Course_id=GetCourses(i).id)
                        list_courses_success.append(i)
                    except:
                        list_fail.append(i)
                if len(list_courses_success) > 0:
                    messages.success(request, f'List of courses added to {request.POST.get("Name")}'
                                              f' class: {list_courses_success}')
                if len(list_fail) > 0:
                    messages.warning(request,
                                     f'List of courses unsuccessfully added to {request.POST.get("Name")}'
                                     f'class: {list_fail}')
            CreateAttendaces(request.POST.get("Name"))
        else:
            messages.warning(
                request, f'Create class {request.POST.get("Name")} unsuccessful!')
        return redirect("ListViewClass")


class UpdateClass(View):
    form = ClassesForm()
    liststudents = []
    listcourses = []

    def get(self, request, Name):
        context = {
            'class': GetClass(Name),
        }
        return render(request, "StaffPage/Classes/Update.html", context=context)

    def post(self, request, Name):
        form = UploadClassesForm(request.POST or None, instance=GetClass(Name))
        if form.is_valid():
            form.save()
            messages.success(request, f'Update class {Name} successful!')
        else:
            messages.warning(request, f'Update class {Name} failed!')
        return redirect('ListViewClass')


# Student in class
class ViewStudentInClass(View):
    def get(self, request, Name):
        context = {
            'class': GetClass(Name),
            'students': paginators(request, GetClass(Name).students_set.all())
        }
        return render(request, "StaffPage/Classes/Students/ViewStudentsInClass.html", context=context)


class AddStudentToClass(View):
    def get(self, request, Class):
        context = {
            'class': GetClass(Class),
            'studentNoneClass': Students.objects.filter(Class=None, admin__faculty=request.user.faculty, admin__is_active=True),
            'studentInClass': Students.objects.filter(Class__Name=Class),
        }
        return render(request, "StaffPage/Classes/Students/AddStudentsToClass.html", context=context)

    def post(self, request, Class):
        liststudentsInClass = []
        list_students_success = []
        students = request.POST.getlist('username')
        for item in GetClass(Class).students_set.all():
            liststudentsInClass.append(item.admin.username)
        listStudentRemove = []
        if students != liststudentsInClass:
            if len(liststudentsInClass) > 0:
                for i in range(0, len(liststudentsInClass)):
                    if liststudentsInClass[i] not in students:
                        listStudentRemove.append(liststudentsInClass[i])
                RemoveAttendanceWithStudent(
                    Class, listStudentRemove)
                RemoveStudentInClass(listStudentRemove)
            if len(students) > 0:
                list_fail = []
                for i in students:
                    if i not in liststudentsInClass:
                        form_s = AddStudentForm(request.POST or None,
                                                instance=get_object_or_404(Students, admin__username=i))
                        if form_s.is_valid():
                            form_s = form_s.save(commit=False)
                            form_s.Class = GetClass(Class)
                            form_s.save()
                            list_students_success.append(i)
                        else:
                            list_fail.append(i)
                if len(list_students_success) > 0:
                    messages.success(request, f'List of students added to {request.POST.get("Name")}'
                                              f'class: {list_students_success}')
                if len(list_fail) > 0:
                    messages.warning(request, f'List of students unsuccessfully added to {request.POST.get("Name")}'
                                              f'class: {list_fail}')
            if len(list_students_success) > 0:
                CreateAttendacesWithStudents(Class, list_students_success)
                UpdateAttendance(Class, list_students_success)
        return redirect('ViewStudentInClass', Class)


class UpdateStudentInClass(View):
    def get(self, request, Class, Course):
        context = {
            'trainers': Trainers.objects.all(),
            'ClassCourse': get_object_or_404(ClassCourse, Class=GetClass(Class), Course=GetCourses(Course)),
            'Attendance': Attendance.objects.filter(Student=GetClass(Class).students_set.first(),
                                                    Lesson__Course__Code=Course)
        }
        return render(request, "StaffPage/Classes/Students/UpdateStudentInClass.html", context=context)

    def post(self, request, Class, Course):
        list = []
        lessons = GetCourses(Course).lessons_set.all()
        try:
            form = AddTrainerToClass(request.POST or None,
                                     instance=get_object_or_404(ClassCourse, Class__Name=Class, Course__id=Course))
            if form.is_valid():
                form.save()

            for student in Students.objects.filter(Class=GetClass(Class)):
                for lesson in lessons:
                    attendance = get_object_or_404(
                        Attendance, Lesson=lesson, Student=GetStudent(student))
                    item = AttendanceForm(instance=attendance)
                    item = item.save(commit=False)
                    item.Trainer = ClassCourse.objects.get(
                        Course__id=Course, Class__Name=Class).Trainer
                    if request.POST.get("Date-{}".format(lesson.Name)) != '':
                        item.Date = request.POST.get(
                            "Date-{}".format(lesson.Name))
                    if request.POST.get("StartTime-{}".format(lesson.Name)) != '':
                        item.StartTime = request.POST.get(
                            "StartTime-{}".format(lesson.Name))
                    if request.POST.get("EndTime-{}".format(lesson.Name)) != '':
                        item.EndTime = request.POST.get(
                            "EndTime-{}".format(lesson.Name))
                    item.save()
            messages.success(request, f'Update information success!')
        except:
            messages.warning(request, f'Update information failed!')
        return redirect(f'/StaffPage/Classes/{Class}/{Course}/Update/')


# Course in class
class ViewCourseInClass(View):
    def get(self, request, Name):
        data = ClassCourse.objects.filter(Class__Name=Name)
        result = []
        for item in data:
            result.append({
                'Class': item.Class.Name,
                'Course': item.Course,
                'Code': item.Course.Code,
                'Lessons': item.Course.lessons_set.all().count(),
                'Time':  item.attendance_set.filter(Lesson__Session=1).first().Slot.StartTime if item.attendance_set.filter(Lesson__Session=1).count() > 0 and item.attendance_set.filter(Lesson__Session=1).first().Slot != None else '',
                'Date': item.attendance_set.filter(Lesson__Session=1).first().Date.strftime('%d/%m/%Y') if item.attendance_set.filter(Lesson__Session=1).count() > 0 and item.attendance_set.filter(Lesson__Session=1).first().Date != None else "Not yet",
                'Trainer': item.Trainer,
            })
        seen = set()
        new_l = []
        for d in result:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        context = {
            'class': GetClass(Name),
            'courses': paginators(request, result)
        }
        return render(request, "StaffPage/Classes/Courses/CoursesInClass.html", context=context)


class AddCourseToClass(View):
    def get(self, request, Class):
        context = {
            'class': GetClass(Class),
            'coursesNoneClass': CoursesNoneClass(Class, request.user.faculty),
            'coursesInClass': ClassCourse.objects.filter(Class__Name=Class),
        }
        return render(request, "StaffPage/Classes/Courses/AddCourseToClass.html", context=context)

    def post(self, request, Class):
        allCourseInClas = []
        list_courses_success = []
        courses = request.POST.getlist('Courses')
        for item in GetClass(Class).classcourse_set.all():
            allCourseInClas.append(str(item.Course.id))
        ListCourseRemove = []
        # ADD Students
        # Add Courses
        if courses != allCourseInClas:
            if len(allCourseInClas) > 0:
                for i in range(0, len(allCourseInClas)):
                    if allCourseInClas[i] not in courses:
                        ListCourseRemove.append(allCourseInClas[i])
                RemoveAttendanceWithCourse(Class, ListCourseRemove)
                RemoveCoursesInClass(Class, ListCourseRemove)
            if len(courses) > 0:
                list_fail = []
                for i in courses:
                    if i not in allCourseInClas:
                        try:
                            classcourse = ClassCourse.objects.create(Class_id=GetClass(Class).id,
                                                                     Course_id=GetCourses(i).id)
                            list_courses_success.append(i)
                        except:
                            list_fail.append(i)
                messages.success(request, f'The course list has been successfully updated! '
                                          f'class: {Class}')
            else:
                messages.success(request, f'Deleted full course from '
                                          f'class: {Class}')
            CreateAttendacesWithCourse(Class, list_courses_success)
        return redirect(f'/StaffPage/Classes/{Class}/AddCourse')


class UpdateCourseInClass(View):
    def get(self, request, Class, Course):
        context = {
            'trainers': Trainers.objects.filter(admin__faculty=request.user.faculty),
            'Slot': Slots.objects.all().order_by("Slot"),
            'ClassCourse': get_object_or_404(ClassCourse, Class=GetClass(Class), Course__id=Course),
            'Classroom': ClassRoom.objects.all().order_by("Name"),
            'Attendance': Attendance.objects.filter(Student=GetClass(Class).students_set.first(),
                                                   ClassCourse_id=ClassCourse.objects.get(Class__Name=Class, Course__id=Course)).order_by("Lesson__Session"),
            'attendance': Attendance.objects.filter(Student=GetClass(Class).students_set.first(),
                                                   ClassCourse_id=ClassCourse.objects.get(Class__Name=Class, Course__id=Course), Slot__isnull=True, ClassRoom__isnull=True)
        }
        return render(request, "StaffPage/Classes/Courses/UpdateCourseInClass.html", context=context)

    def post(self, request, Class, Course):
        lessons = GetCourses(Course).lessons_set.all()
        form = AddTrainerToClass(request.POST or None,
                                 instance=get_object_or_404(ClassCourse, Class__Name=Class, Course__id=Course))
        if form.is_valid():
            form.save()
        for student in Students.objects.filter(Class=GetClass(Class)):
            for lesson in lessons:
                item = get_object_or_404(
                    Attendance, Lesson=lesson, Student=GetStudent(student.admin.username))
                if request.POST.get("Date-{}".format(lesson.id)) != '':
                    Date = datetime.strptime(request.POST.get(
                        "Date-{}".format(lesson.id)), '%d/%m/%Y')
                    item.Date = Date
                if request.POST.get("Classroom-{}".format(lesson.id)) != '' and request.POST.get("Classroom-{}".format(lesson.id)) != '-- Choose a Room --':
                    item.ClassRoom = ClassRoom.objects.get(
                        id=request.POST.get("Classroom-{}".format(lesson.id)))
                if request.POST.get("Slot-{}".format(lesson.id)) != '' and request.POST.get("Slot-{}".format(lesson.id)) != '-- Choose a Slot --':
                    item.Slot = Slots.objects.get(
                        id=request.POST.get("Slot-{}".format(lesson.id)))
                b = Attendance.objects.filter(Date=item.Date, ClassRoom=item.ClassRoom, Slot=item.Slot)
                if b.count() > 0:
                    a = 0
                    for i in b:
                        if i.id == item.id:
                            continue
                        elif i.ClassCourse_id == item.ClassCourse_id and i.Lesson_id == item.Lesson_id:
                            continue
                        else:
                            a += 1
                    if a > 0:
                        messages.warning(request, f'The schedule cannot be changed because the {item.Lesson.Name}\'s'
                                                  f' schedule has been coincided.')
                        return redirect(f'/StaffPage/Classes/{Class}/{Course}/Update/')
                item.save()
        messages.success(request, f'Update information success!')
        return redirect(f'/StaffPage/Classes/{Class}/{Course}/Update/')


class StatisticsOfCoursesInClass(View):
    def get(self, request, Class, Course):
        attendance = Attendance.objects.filter(
            Student__Class__Name=Class, Lesson__Course__Code=Course)

        context = {
            'attendance': attendance,
        }
        return render(request, "StaffPage/Classes/Courses/StatisticsOfCoursesInClass.html", context=context)


class ScheduleOfCoursesInClass(View):
    def get(self, request, Class, Course):
        context = {
        }
        return render(request, "StaffPage/Classes/Courses/GenerateScheduleForCourseInClass.html", context=context)

    def post(self, request, Class, Course):
        Schedule = ScheduleForCourseForm(request.POST)
        if Schedule.is_valid():
            data = (request, GetClass(Class).id,
                    Schedule.cleaned_data["LessonsPerWeek"], Schedule.cleaned_data["startTime"], Course)
            population = Population(4, data)
            population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
            geneticAlgorithm = GeneticAlgorithm()
            while (population.get_schedules()[0].get_fitness() != 1.0):
                population = geneticAlgorithm.evolve(population, data)
                population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
            pop = population.get_schedules()[0]
            _classcourse = pop._Classcourse
            _attendance = pop._Attendance
            for i in range(0, len(_classcourse)):
                classcourse = ClassCourse.objects.get(id=_classcourse[i].id)
                classcourse.Trainer_id = _classcourse[i].Trainer_id
                classcourse.save()
                for j in range(0, len(_attendance)):
                    if _attendance[j].ClassCourse_id == classcourse.id:
                        attendance = Attendance.objects.get(Student_id=_attendance[j].Student_id,
                                                            Lesson_id=_attendance[j].Lesson_id,
                                                            ClassCourse_id=_attendance[j].ClassCourse_id)
                        attendance.ClassRoom_id = _attendance[j].ClassRoom_id
                        attendance.Slot_id = _attendance[j].Slot_id
                        attendance.Date = _attendance[j].Date
                        attendance.save()
            messages.success(request, f'Success')
        return redirect(f'/StaffPage/Classes/{Class}/{Course}/Update/')

# Profile
class StaffProfile(View):
    def get_user(self, request):
        return CustomUser.objects.get(id=request.user.id)

    def get(self, request):
        context = {
            'user': self.get_user(request),
        }
        return render(request, "StaffPage/Profile/Profile.html", context=context)

    def post(self, request):
        if request.POST.get('_ChangeProfile') != None:
            form = UserUpdateForm(request.POST)
            if form.is_valid():

                email = form.cleaned_data["email"]
                address = form.cleaned_data["address"]
                telephone = form.cleaned_data["telephone"]
                birthday = form.cleaned_data["birthday"]
                if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists() and request.user.email != email:
                    messages.warning(request, f'Email already exists!')
                    return redirect('StaffProfile')
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"]).exists() and request.user.telephone != telephone:
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('StaffProfile')


                try:
                    # save CustomUser
                    user = CustomUser.objects.get(id=request.user.id)
                    user.email = email
                    user.address = address
                    user.telephone = telephone
                    user.birthday = birthday
                    if request.FILES.get('Avatar') is not None:
                        user.Avatar = StorageImage.SaveImage(id=user.id,
                                                             image=request.FILES.get('Avatar'),
                                                             url=f'Avatar/{user.user_type}')
                    user.save()
                    messages.success(
                        request, f'Profile of {request.user.username} has been updated!')
                except:
                    messages.warning(
                        request, f'Profile of {request.user.username} update failed!')
            else:
                messages.warning(
                    request, f'Profile of {request.user.username} update failed!')
            return redirect('StaffProfile')
        elif request.POST.get('_ChangePassword') != None:
            form = ChangePassword(request.POST)
            if form.is_valid():
                oldpassword = form.cleaned_data["oldpassword"]
                newpassword = form.cleaned_data["newpassword"]
                confirmpassword = form.cleaned_data["confirmpassword"]
                try:
                    if oldpassword != None and newpassword != None and newpassword == confirmpassword:
                        saveuser = CustomUser.objects.get(id=request.user.id)
                        if request.user.check_password(oldpassword):
                            saveuser.set_password(newpassword)
                            saveuser.save()
                            SendMailChangePassword(
                                request.user.email, request.user.username)
                            messages.success(
                                request, f'Password of {request.user.username} has been updated!')
                        else:
                            messages.warning(
                                request, f'Old password is not wrong!')
                except:
                    messages.warning(
                        request, f'Password of {request.user.username} update failed!')
            else:
                messages.warning(
                    request, f'Password of {request.user.username} update failed!')
            return redirect('StaffProfile')


class Calendar(View):
    def get(self, request):
        data = Attendance.objects.filter(
            ClassCourse__Class__faculty=request.user.faculty)
        result = []
        for item in data:
            if item.Date != None:
                result.append({
                    'Trainer': item.ClassCourse.Trainer.admin.username,
                    'Lesson': item.Lesson,
                    'Class': item.Student.Class.Name,
                    'Code': item.Lesson.Course.Code,
                    'Course': item.Lesson.Course.Name,
                    'Date': item.Date,
                    'StartTime': item.Slot.StartTime,
                    'EndTime': item.Slot.EndTime,
                    'Classroom': item.ClassRoom.Name,
                })
        seen = set()
        new_l = []
        for d in result:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        context = {
            'courses': ClassCourse.objects.filter(Course__faculty=request.user.faculty),
            'data': data,
            'result': new_l,
            'timenow': datetime.now().date(),
        }
        return render(request, "StaffPage/Calendar/index.html", context=context)


class ScheduleForClass(View):
    def get(self, request):
        classes = Classes.objects.filter(faculty__Name=request.user.faculty)
        classcourse = ClassCourse.objects.filter(
            Class__faculty__Name=request.user.faculty)
        attendances = Attendance.objects.all()
        _Class = []
        for c in classes:
            for cs in classcourse.filter(Class_id=c.id):
                for a in attendances.filter(ClassCourse_id=cs.id):
                    if a.Date == None:
                        _Class.append(a.ClassCourse.Class)
                        break
        context = {
            'classes': list(dict.fromkeys(_Class)),
        }
        return render(request, "StaffPage/Calendar/ScheduleForClass.html", context=context)

    def post(self, request):
        Schedule = ScheduleForm(request.POST)
        if Schedule.is_valid():
            data = (request, Schedule.cleaned_data["Class"],
                    Schedule.cleaned_data["LessonsPerWeek"],  Schedule.cleaned_data["startTime"], None)
            population = Population(4, data)
            population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
            geneticAlgorithm = GeneticAlgorithm()
            while (population.get_schedules()[0].get_fitness() != 1.0):
                population = geneticAlgorithm.evolve(population, data)
                population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
            pop = population.get_schedules()[0]
            _classcourse = pop._Classcourse
            _attendance = pop._Attendance
            for i in range(0, len(_classcourse)):
                classcourse = ClassCourse.objects.get(id=_classcourse[i].id)
                classcourse.Trainer_id = _classcourse[i].Trainer_id
                classcourse.save()
                for j in range(0, len(_attendance)):
                    if _attendance[j].ClassCourse_id == classcourse.id:
                        attendance = Attendance.objects.get(Student_id=_attendance[j].Student_id, Lesson_id=_attendance[j].Lesson_id, ClassCourse_id=_attendance[j].ClassCourse_id)
                        attendance.ClassRoom_id = _attendance[j].ClassRoom_id
                        attendance.Slot_id = _attendance[j].Slot_id
                        attendance.Date = _attendance[j].Date
                        attendance.save()
            messages.success(request, f'Success')
        return redirect("CalendarForStaff")
