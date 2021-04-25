from django.template.defaultfilters import register

import os
from os import listdir
from os.path import isfile, join
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from API.models import (Students, ClassCourse, Attendance, Slots, CustomUser)
from App.Define import (GetLessons, GetStatusAttendance,
                        GetStudent, GetCourses, SendMailChangePassword)
from App.forms import (AttendanceForm, StatusAttendanceForm, UserUpdateForm, ChangePassword)
from FaceAPI import FaceAPI
from datetime import date, datetime, timedelta
from StudentManagementSystem import settings
from FaceAPI.FireBase import StorageImage


@register.filter
def GetImage(value):
    return StorageImage.GetImage(value)

class TrainerPage(View):
    def get(self, request):
        data = Attendance.objects.filter(
            ClassCourse__Trainer__admin_id=request.user.id)
        result = []
        for item in data:
            result.append({
                'Lesson': item.Lesson,
                'Class': item.Student.Class.Name,
                'Code': item.Lesson.Course,
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
            'result': new_l,
            'timenow': date.today(),
        }
        return render(request, 'TrainerPage/index.html', context)

class trainer_profile(View):
    def get_user(self, request):
        return CustomUser.objects.get(id=request.user.id)

    def get(self, request):
        context = {
            'user': self.get_user(request),
        }
        return render(request,"TrainerPage/Profile/Profile.html", context=context)

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
                    return redirect('trainer_profile')
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"]).exists() and request.user.telephone != telephone:
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('trainer_profile')


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
                        request, f'Profile has been updated!')
                except:
                    messages.warning(
                        request, f'Profile update failed!')
            else:
                messages.warning(
                    request, f'Profile update failed!')
            return redirect('trainer_profile')
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
            return redirect('trainer_profile')

class Attendances(View):
    students = Students.objects.all()

    def get(self, request, Class, Course, Lesson):
        images = []
        if os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{Lesson}/faces/'):
            for i in listdir(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{Lesson}/faces/'):
                if isfile(join(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{Lesson}/faces/', i)):
                    images.append({'image': i, 'username': i.replace('.png', '')})
        context = {
            'Class': Class,
            'Course': GetCourses(Course),
            'Lesson': GetLessons(Lesson),
            'students': Attendance.objects.filter(Student__Class__Name=Class, Lesson__Course__id=Course,
                                                  Lesson_id=Lesson),
            'images': images,
        }
        return render(request, "TrainerPage/Attendances/index.html", context=context)

    def post(self, request, Class, Course, Lesson):
        if request.POST.get('_Save') == 'AddImage':
            for i in request.FILES.getlist('Url'):
                FaceAPI.saveImageClassroom(Class, Course, Lesson, i)
            try:
                for j in FaceAPI.dectectClassImages(Class, Course, Lesson):
                    if not Students.objects.filter(admin__username=j).exists():
                        continue
                    attendance = Attendance.objects.get(Student_id=Students.objects.get(admin__username=j).id,
                                                        Lesson_id=Lesson,
                                                        ClassCourse_id=ClassCourse.objects.get(Class__Name=Class, Course__id=Course).id)
                    attendance.Status_id = GetStatusAttendance('Present').id
                    attendance.save()

                messages.success(request, f'Attendance is successful!')
            except:
                messages.warning(request, f'Faild!')
        elif request.POST.get('_Save') == 'Save':
            try:
                for student in request.POST.getlist("Students"):
                    attendance = Attendance.objects.get(Student_id=GetStudent(student).id, Lesson_id=Lesson,
                                                        ClassCourse_id=ClassCourse.objects.get(Class__Name=Class,
                                                                                               Course__id=Course).id)
                    attendance.Status_id = GetStatusAttendance(
                        request.POST.get("Attendance-{}".format(student))).id
                    attendance.save()
                messages.success(request, f'Attendance is successful!')
            except:
                messages.warning(request, f'Attendance was not successful!')
        return redirect(f'/TrainerPage/Attendance/{Class}/{Course}/{Lesson}')

class ViewMyCourses(View):
    def get(self, request):
        data = ClassCourse.objects.filter(Trainer__admin__username=request.user.username)
        result = []
        for item in data:
            result.append({
                'Class': item.Class.Name,
                'Course': item.Course,
                'StartDate': item.attendance_set.filter(Lesson__Session=1).first().Date.strftime('%d/%m/%Y') if item.attendance_set.filter(Lesson__Session=1).count() > 0 and item.attendance_set.filter(Lesson__Session=1).first().Date != None else "Not yet",
                'EndDate': item.attendance_set.order_by('Lesson__Session').last().Date.strftime('%d/%m/%Y') if item.attendance_set.order_by('Lesson__Session').last().Date != None else "Not yet",
            })
        seen = set()
        new_l = []
        for d in result:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        context = {
            'courses': result
        }
        return render(request, "TrainerPage/Courses/TrainerViewCourses.html", context=context)

#
# class TrainerPage(View):
#     def get(self, request):
#         data = Attendance.objects.filter(Trainer__admin_id=request.user.id)
#         json = requests.get(f'http://127.0.0.1:8000/api/ViewAttendance/{request.user.id}')
#         context = {
#             'courses': ClassCourse.objects.filter(Trainer__admin_id=request.user.id),
#             'data': data,
#             'result': json.json(),
#             'timenow': date.today(),
#         }
#         return render(request, 'Trainer/index.html', context)
# #
