from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from API.models import CustomUser, Staffs, Students, Attendance, Courses, ClassCourse
from App.Define import (paginators, GetStudent, RandomPassword,
                        GetUsernameFromFullnameStudent, GetNameFromFullname, SendMailChangePassword, )
from App.forms import (StudentStatus, UserUpdateForm, ImageStudent,
                       UploadAvatar, UserCreateForm, ChangePassword, )
from FaceAPI import FaceAPI
import hashlib
import time

from FaceAPI.FireBase import StorageImage


class StudentPage(View):
    def get(self, request):
        student_obj = Students.objects.get(admin_id=request.user.id)
        attendance_future = Attendance.objects.filter(Student_id=student_obj.id, Status__Status='Not Yet').count()
        attendance_present = Attendance.objects.filter(Student_id=student_obj.id, Status__Status='Present').count()
        attendance_absent = Attendance.objects.filter(Student_id=student_obj.id, Status__Status='Absent').count()
        courses = Courses.objects.filter(classcourse__Class__id=student_obj.Class_id).count()
        course_name = []
        data_present = []
        data_absent = []
        course_data = ClassCourse.objects.filter(Class_id=student_obj.Class_id)
        for ClassCourses in course_data:
            attendance = Attendance.objects.filter(Student_id=student_obj.id, ClassCourse_id=ClassCourses.id)
            attendance_present_count = attendance.filter(Status__Status='Present').count()
            attendance_absent_count = attendance.filter(Status__Status='Absent').count()
            course_name.append(ClassCourses.Course.Name)
            data_present.append(attendance_present_count)
            data_absent.append(attendance_absent_count)
        context = {"attendance_future": attendance_future,
                   "attendance_absent": attendance_absent,
                   "attendance_present": attendance_present,
                   "courses": courses,
                   "data_name": course_name,
                   "data1": data_present,
                   "data2": data_absent,
                   }
        return render(request, "StudentPage/index.html", context=context)


class StudentViewCourses(View):
    def get(self, request):
        student_obj = Students.objects.get(admin_id=request.user.id)
        data = ClassCourse.objects.filter(Class_id=student_obj.Class_id)
        result = []
        for item in data:
            result.append({
                'Class': item.Class.Name,
                'Course': item.Course,
                'Code': item.Course.Code,
                'Lessons': item.Course.lessons_set.all().count(),
                'StartDate': item.attendance_set.filter(Lesson__Session=1).first().Date.strftime('%d/%m/%Y') if item.attendance_set.filter(Lesson__Session=1).count() > 0 and item.attendance_set.filter(Lesson__Session=1).first().Date != None else "Not yet",
                'EndDate': item.attendance_set.order_by('Lesson__Session').last().Date.strftime('%d/%m/%Y') if item.attendance_set.order_by('Lesson__Session').last().Date != None else "Not yet",
                'Trainer': item.Trainer,
                'Attendance_total': item.attendance_set.all().count(),
                'Attendance_present': item.attendance_set.filter(Status__Status='Present').count(),
                'Attendance_absent': item.attendance_set.filter(Status__Status='Absent').count(),
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
        return render(request, "StudentPage/Courses/StudentViewCourses.html", context=context)


class StudentViewTimeTable(View):
    def get(self, request):
        student_obj = Students.objects.get(admin_id=request.user.id)
        data = Attendance.objects.filter(Student_id=student_obj.id)
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
                'Trainer': GetNameFromFullname(item.ClassCourse.Trainer.admin.first_name +' '+ item.ClassCourse.Trainer.admin.last_name),
                'Status': item.Status.Status,
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
        return render(request, "StudentPage/Timetable/index.html", context=context)

class student_view_attendance(View):
    def get(self, request, Course):
        student=Students.objects.get(admin=request.user.id)
        course=Courses.objects.get(id=Course)
        attendances = Attendance.objects.filter(Student_id=student.id, ClassCourse__Course__id=Course, ClassCourse__Class__id=student.Class_id).order_by('Lesson__Session')
        attendances_absent = Attendance.objects.filter(id__in=attendances, Status__Status='Absent')
        attendances_percent = attendances_absent.count()/attendances.count()*100
        context = {
            'student': student,
            'course': course,
            'attendances': attendances,
            'attendances_absent':attendances_absent,
            'attendances_percent': attendances_percent.__round__(2),
        }
        return render(request,"StudentPage/student_attendance.html",context=context)

class student_profile(View):
    def get_user(self, request):
        return CustomUser.objects.get(id=request.user.id)

    def get(self, request):
        context = {
            'user': self.get_user(request),
            'images': ImageStudent.objects.filter(Student_id=self.get_user(request).students.id),
        }
        return render(request,"StudentPage/Profile/student_profile.html", context=context)

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
                    return redirect('student_profile')
                if CustomUser.objects.filter(
                        telephone=form.cleaned_data["telephone"]).exists() and request.user.telephone != telephone:
                    messages.warning(request, f'Telephone already exists!')
                    return redirect('student_profile')
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
        elif request.POST.get('_Save') == 'AddImage':
            listimage = []
            for i in request.FILES.getlist('Url'):
                faceid = FaceAPI.face_client.person_group_person.add_face_from_stream(FaceAPI.PERSON_GROUP_ID,
                                                                                      GetStudent(request.user.username).PersonId, i)
                image = ImageStudent(Student_id=GetStudent(request.user.username).id,
                                     Url=StorageImage.SaveImage(id=GetStudent(request.user.username).id, image=i, url="ImageStudent"),
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
                messages.warning(request, f'Upload images failed!')
        elif request.POST.get('_DeleteImage') == 'DeleteImage':
            try:
                img = ImageStudent.objects.get(id=request.POST.get('id'))
                FaceAPI.DeleteImage(img.Url, Students.objects.get(id=img.Student.id).PersonId, img.FaceId)
                img.delete()
                FaceAPI.TrainPersonGroup()
                messages.success(request, f'Delete images success!')
            except:
                messages.warning(request, f'Delete images unsuccessful!')
        return redirect('student_profile')

@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student.id)
    return render(request,"student_template/all_notification.html",{"notifications":notifications})

def student_view_result(request):
    student=Students.objects.get(admin=request.user.id)
    studentresult=StudentResult.objects.filter(student_id=student.id)
    return render(request,"student_template/student_result.html",{"studentresult":studentresult})