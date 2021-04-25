from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from API.models import (CustomUser, Staffs, Students, ImageStudent,
                        Trainers, Classes, Courses, Lessons, ClassCourse,
                        StatusAttendance, Attendance, Faculties, Slots, ClassRoom)
from App.Define import (paginators, GetStudent, GetCustomUser, RandomPassword,
                        GetUsernameFromFullnameStudent, GetUsernameFromFullnameStaff, GetTrainer, GetCodeForCourse,
                        GetUsernameFromFullnameTrainer, GetClass, CoursesNoneClass,
                        GetCourses, CreateAttendaces, RemoveAttendanceWithStudent,
                        RemoveStudentInClass, CreateAttendacesWithStudents, RemoveAttendanceWithCourse,
                        RemoveCoursesInClass, CreateAttendacesWithCourse, SendMailCreateAccount,
                        SendMailChangePassword
                        )
from App.forms import (StaffStatus, UserUpdateForm, ImageStudent, CourseStatus,
                       UploadAvatar, UserCreateForm, CourseForm,
                       TrainerStatus, ClassesForm, AddStudentForm, AddCoursesForm, AddTrainerToClass,
                       AttendanceForm, ChangePassword, FacultyForm, SlotsForm, ClassRoomForm)
from datetime import datetime

from FaceAPI.FireBase import StorageImage


class AdminPage(View):
    def get(self, request):
        faculty_count = Faculties.objects.all().count()
        staff_count = Staffs.objects.all().count()
        class_count = Classes.objects.all().count()
        course_count = Courses.objects.all().count()

        context = {
            'staff_count': staff_count,
            'faculty_count': faculty_count,
            'class_count': class_count,
            'course_count': course_count,
        }
        return render(request, "AdminPage/index.html",context=context)


# Staff list view
class ListViewAccountStaff(View):
    Staffs = CustomUser.objects.filter(user_type=2)

    def get(self, request):
        context = {
            'staffs': paginators(request, self.Staffs),
        }
        return render(request, "AdminPage/Staffs/ListView.html", context=context)

    def post(self, request):
        form = StaffStatus(request.POST or None, instance=GetCustomUser(
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
        return redirect(f'/AdminPage/Staffs/')


# Create account staff
class CreateAccountStaff(View):
    def get(self, request):
        context = {
            'faculties': Faculties.objects.all(),
        }
        return render(request, "AdminPage/Staffs/Create.html", context=context)

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists():
                messages.warning(request, f'Email already exists!')
                return redirect('ListViewAccountStaff')
            if CustomUser.objects.filter(telephone=form.cleaned_data["telephone"].replace(" ", "")).exists():
                messages.warning(request, f'Telephone already exists!')
                return redirect('ListViewAccountStaff')
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            fullname = first_name + " " + last_name
            username = GetUsernameFromFullnameStaff(request, fullname)
            password = RandomPassword(8)
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            telephone = form.cleaned_data["telephone"].replace(" ", "")
            birthday = form.cleaned_data["birthday"]
            faculty = form.cleaned_data["faculty"]
            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      last_name=last_name, first_name=first_name, address=address,
                                                      telephone=telephone, birthday=birthday, faculty_id=faculty, user_type=2)

                staff = Staffs.objects.create(admin_id=user.id)
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
                return redirect('ProfileAccountStaffs', username)
            except:
                user = CustomUser.objects.filter(username=username)
                if user.exists():
                    CustomUser.delete(
                        CustomUser.objects.get(username=username))
                if Staffs.objects.filter(admin_id=user).exists():
                    Staffs.delete(Staffs.objects.get(admin_id=user))
                messages.warning(request, f'Staff account creation failed')
                return redirect('ListViewAccountStaff')
        else:
            messages.warning(request, f'Staff account creation failed')
        return redirect('ListViewAccountStaff')


# Update account staff
class UpdateAccountStaff(View):
    def get(self, request, Username):
        context = {
            'staff': get_object_or_404(CustomUser, username=Username),
            'faculties': Faculties.objects.all()
        }
        return render(request, "AdminPage/Staffs/Update.html", context=context)

    def post(self, request, Username):
        form = UserUpdateForm(request.POST)
        if form.is_valid():
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
                                                           url=f'Avatar/{GetCustomUser(Username).user_type}')
                    avatar.save()
                messages.success(
                    request, f'Profile of {Username} has been updated!')
                return redirect('ProfileAccountStaffs', Username)
            except:
                messages.warning(
                    request, f'Profile of {Username} update failed!')
        else:
            messages.warning(request, f'Profile of {Username} update failed!')
        return redirect(f'ProfileAccountStaffs')


# faculty
class ListViewFaculty(View):
    faculties = Faculties.objects.all()

    def get(self, request):
        context = {
            'faculties': paginators(request, self.faculties)
        }
        return render(request, "AdminPage/Faculty/ListView.html", context=context)


class CreateFaculty(View):
    def get(self, request):
        return render(request, "AdminPage/Faculty/Create.html")

    def post(self, request):
        form = FacultyForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Create faculty {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Create faculty {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewFaculty')


class UpdateFaculty(View):
    form = FacultyForm()

    def get(self, request, name):
        context = {
            'faculty': Faculties.objects.get(Name=name),
        }
        return render(request, "AdminPage/Faculty/Update.html", context=context)

    def post(self, request, name):
        form = FacultyForm(request.POST or None,
                           instance=Faculties.objects.get(Name=name))
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Update faculty {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Update faculty {request.POST.get("Name")} unsuccessful!')
        return redirect('UpdateFaculty', name)


# Slots
class ListViewSlots(View):
    slots = Slots.objects.all().order_by("Slot")

    def get(self, request):
        context = {
            'slots': paginators(request, self.slots)
        }
        return render(request, "AdminPage/Slot/ListView.html", context=context)


class CreateSlots(View):
    def get(self, request):
        return render(request, "AdminPage/Slot/Create.html")

    def post(self, request):
        form = SlotsForm(request.POST or None)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, f'Create slot {request.POST.get("Name")} successful!')
            except:
                messages.warning(
                    request, f'Create slot {request.POST.get("Name")} unsuccessful!')
        else:
            messages.warning(
                request, f'Create slot {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewSlot')


class UpdateSlots(View):
    form = SlotsForm()

    def get(self, request, id):
        context = {
            'slots': Slots.objects.get(id=id),
        }
        return render(request, "AdminPage/Slot/Update.html", context=context)

    def post(self, request, id):
        form = SlotsForm(request.POST or None)
        if form.is_valid():
            slots = Slots.objects.get(id=id)
            slots.Slot = form.cleaned_data["Slot"]
            slots.StartTime = form.cleaned_data["StartTime"]
            slots.EndTime = form.cleaned_data["EndTime"]
            slots.save()
            messages.success(
                request, f'Update slot {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Update slot {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewSlot')


class DeleteSlots(View):
    def post(self, request, id):
        try:
            slots = Slots.objects.get(id=id)
            slots.delete()
            messages.success(request, f'delete slot successful!')
        except:
            messages.warning(request, f'delete slot unsuccessful!')
        return redirect('ListViewSlot')

# ClassRoom


class ListViewClassRoom(View):
    classroom = ClassRoom.objects.all().order_by("Name")

    def get(self, request):
        context = {
            'classroom': paginators(request, self.classroom)
        }
        return render(request, "AdminPage/ClassRoom/ListView.html", context=context)


class CreateClassRoom(View):
    def get(self, request):
        return render(request, "AdminPage/ClassRoom/Create.html")

    def post(self, request):
        form = ClassRoomForm(request.POST or None)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, f'Create classroom {request.POST.get("Name")} successful!')
            except:
                messages.warning(
                    request, f'Create classroom {request.POST.get("Name")} unsuccessful!')
        else:
            messages.warning(
                request, f'Create slot {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewClassRoom')


class UpdateClassRoom(View):
    form = ClassRoomForm()

    def get(self, request, id):
        context = {
            'classroom': ClassRoom.objects.get(id=id),
        }
        return render(request, "AdminPage/ClassRoom/Update.html", context=context)

    def post(self, request, id):
        form = ClassRoomForm(request.POST or None)
        if form.is_valid():
            classroom = ClassRoom.objects.get(id=id)
            classroom.Name = form.cleaned_data["Name"]
            classroom.save()
            messages.success(
                request, f'Update classroom {request.POST.get("Name")} successful!')
        else:
            messages.warning(
                request, f'Update classroom {request.POST.get("Name")} unsuccessful!')
        return redirect('ListViewClassRoom')


class DeleteClassRoom(View):
    def post(self, request, id):
        try:
            classroom = ClassRoom.objects.get(id=id)
            classroom.delete()
            messages.success(request, f'delete slot successful!')
        except:
            messages.warning(request, f'delete slot unsuccessful!')
        return redirect('ListViewClassRoom')

# Profile


class AdminProfile(View):
    def get_user(self, Username):
        return CustomUser.objects.get(username=Username)

    def get(self, request, Username):
        context = {
            'user': self.get_user(Username),
        }
        return render(request, "AdminPage/Profile/Profile.html", context=context)

    def post(self, request, Username):
        if request.POST.get('_ChangeProfile') != None:
            form = UserUpdateForm(request.POST)
            if form.is_valid():

                email = form.cleaned_data["email"]
                address = form.cleaned_data["address"]
                telephone = form.cleaned_data["telephone"]
                birthday = form.cleaned_data["birthday"]
                if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists() and request.user.email != email:
                    messages.warning(request, f'Email already exists!')
                    return redirect('AdminProfile', Username)
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"]).exists() and request.user.telephone != telephone:
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('AdminProfile', Username)
                try:
                    # save CustomUser
                    user = CustomUser.objects.get(id=request.user.id)
                    user.email = email
                    user.address = address
                    user.telephone = telephone
                    user.birthday = birthday
                    user.save()
                    if request.FILES.get('Avatar') is not None:
                        avatar = UploadAvatar(request.FILES, instance=user)
                        avatar = avatar.save(commit=False)
                        avatar.Avatar = request.FILES.get('Avatar')
                        avatar.save()
                except:
                    messages.warning(
                        request, f'Profile of {request.user.username} update failed!')
                messages.success(
                    request, f'Profile of {request.user.username} has been updated!')
            else:
                messages.warning(
                    request, f'Profile of {request.user.username} update failed!')
            return redirect('AdminProfile', Username)
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
            return redirect('AdminProfile', Username)


class Profile(View):
    def get_user(self, Username):
        return CustomUser.objects.get(username=Username)

    def get(self, request, Username):
        context = {
            'user': self.get_user(Username),
        }
        return render(request, "AdminPage/Profile/StaffProfile.html", context=context)

    def post(self, request, Username):
        if request.POST.get('_ChangeProfile') != None:
            form = UserUpdateForm(request.POST)
            if form.is_valid():

                email = form.cleaned_data["email"]
                address = form.cleaned_data["address"]
                telephone = form.cleaned_data["telephone"]
                birthday = form.cleaned_data["birthday"]
                if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists() and request.user.email != email:
                    messages.warning(request, f'Email already exists!')
                    return redirect('ProfileAccountStaffs', Username)
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"]).exists() and request.user.telephone != telephone:
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('ProfileAccountStaffs', Username)
                try:
                    # save CustomUser
                    user = CustomUser.objects.get(id=request.user.id)
                    user.email = email
                    user.address = address
                    user.telephone = telephone
                    user.birthday = birthday
                    user.save()
                    if request.FILES.get('Avatar') is not None:
                        avatar = UploadAvatar(request.FILES, instance=user)
                        avatar = avatar.save(commit=False)
                        avatar.Avatar = request.FILES.get('Avatar')
                        avatar.save()
                except:
                    messages.warning(
                        request, f'Profile of {request.user.username} update failed!')
                messages.success(
                    request, f'Profile of {request.user.username} has been updated!')
            else:
                messages.warning(
                    request, f'Profile of {request.user.username} update failed!')
            return redirect('ProfileAccountStaffs', Username)
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
            return redirect('ProfileAccountStaffs', Username)


class Calendar(View):
    def get(self, request, id):
        data = Attendance.objects.filter(ClassRoom__id=id)
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
                    'Faculty': item.Student.admin.faculty,
                })
        seen = set()
        new_l = []
        for d in result:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        context = {
            'ClassRoom': ClassRoom.objects.get(id=id),
            'data': data,
            'result': new_l,
            'timenow': datetime.now().date(),
        }
        return render(request, "AdminPage/ClassRoom/Calendar/index.html", context=context)
