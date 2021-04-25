import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from StudentManagementSystem import settings
from API.models import CustomUser, Staffs, Students, ImageStudent, Trainers, Classes, Courses, Lessons, ClassCourse, \
    StatusAttendance, Attendance
from App.forms import ClassStudent
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Student and Trainer
def paginators(request, Name):
    return Paginator(Name, 20).get_page(request.GET.get('page'))


def GetStudent(username):
    return get_object_or_404(Students, admin__username=username)


def GetCustomUser(username):
    return get_object_or_404(CustomUser, username=username)


def GetTrainer(username):
    return get_object_or_404(Trainers, admin__username=username)


def GetLastIdStudent():
    if Students.objects.all().count() > 0:
        return Students.objects.all().count() + 1
    else:
        return 1


def CheckEmailAndTelephone(request, email, telephone):
    if CustomUser.objects.filter(email=email).exists():
        messages.warning(request, f'Email already exists!')
        return
    if CustomUser.objects.filter(tele=email).exists():
        messages.warning(request, f'Telephone already exists!')
        return
    pass


def GetLastIdTrainer():
    if Trainers.objects.all().count() > 0:
        return Trainers.objects.all().count() + 1
    else:
        return 1


def GetLastIdStaff():
    if Staffs.objects.all().count() > 0:
        return Staffs.objects.all().count() + 1
    else:
        return 1


def RandomPassword(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits)
                          for i in range(length)))
    return result_str


def remove_accents(full_name):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    s = ''
    for c in full_name:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def GetUsernameFromFullnameStudent(request, fullname):
    full_name = remove_accents(fullname.lower())
    if len(full_name) > 1:
        # split the string into a list
        l = full_name.split()
        username = ""
        # traverse in the list
        for i in range(len(l) - 1):
            s = l[i]
            # adds the capital first character
            username += (s[0].upper())
            # l[-1] gives last item of list l. We
        # use title to print first character in
        # capital.
        number = 0
        if GetLastIdStudent() > 0 and GetLastIdStudent() < 10:
            number = '{}{}'.format(1000, GetLastIdStudent())
        elif GetLastIdStudent() > 9 and GetLastIdStudent() < 100:
            number = '{}{}'.format(100, GetLastIdStudent())
        elif GetLastIdStudent() > 99 and GetLastIdStudent() < 1000:
            number = '{}{}'.format(10, GetLastIdStudent())
        elif GetLastIdStudent() > 999 and GetLastIdStudent() < 10000:
            number = '{}{}'.format(1, GetLastIdStudent())
        username += l[-1].title()
        # first_letter = full_name[0][0]
        # three_letters_surname = full_name[1][0:3]
        # number = '{:03d}'.format(random.randrange(10000, 19999))
        username = 'S{}{}'.format(username, number)
        return username
    else:
        return messages.warning(request, f'Please enter fullname')

def GetNameFromFullname(fullname):
    full_name = remove_accents(fullname.lower())
    if len(full_name) > 1:
        # split the string into a list
        l = full_name.split()
        username = ""
        # traverse in the list
        for i in range(len(l) - 1):
            s = l[i]
            # adds the capital first character
            username += (s[0].upper())
        username += l[-1].title()
        return username

def GetUsernameFromFullnameTrainer(request, fullname):
    full_name = remove_accents(fullname.lower())
    if len(full_name) > 1:
        # split the string into a list
        l = full_name.split()
        username = ""
        # traverse in the list
        for i in range(len(l) - 1):
            s = l[i]
            # adds the capital first character
            username += (s[0].upper())
            # l[-1] gives last item of list l. We
        # use title to print first character in
        # capital.
        number = 0
        if GetLastIdTrainer() > 0 and GetLastIdTrainer() < 10:
            number = '{}{}'.format(1000, GetLastIdTrainer())
        elif GetLastIdTrainer() > 9 and GetLastIdTrainer() < 100:
            number = '{}{}'.format(100, GetLastIdTrainer())
        elif GetLastIdTrainer() > 99 and GetLastIdTrainer() < 1000:
            number = '{}{}'.format(10, GetLastIdTrainer())
        elif GetLastIdTrainer() > 999 and GetLastIdTrainer() < 10000:
            number = '{}{}'.format(1, GetLastIdTrainer())
        username += l[-1].title()
        # first_letter = full_name[0][0]
        # three_letters_surname = full_name[1][0:3]
        # number = '{:03d}'.format(random.randrange(10000, 19999))
        username = 'T{}{}'.format(username, number)
        return username
    else:
        return messages.warning(request, f'Please enter fullname')


def SendMailCreateAccount(email, username, password):
    html_message = render_to_string('MailPage/CreateAccount.html',
                                    {'username': username, 'password': password, 'email': email})
    plain_message = strip_tags(html_message)
    msg = EmailMultiAlternatives(
        'Verify Email', plain_message, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def SendMailChangePassword(email, username):
    html_message = render_to_string(
        'MailPage/ChangePassword.html', {'username': username, 'email': email})
    plain_message = strip_tags(html_message)
    msg = EmailMultiAlternatives(
        'Verify Email', plain_message, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()







def GetUsernameFromFullnameStaff(request, fullname):
    full_name = remove_accents(fullname.lower())
    if len(full_name) > 1:
        # split the string into a list
        l = full_name.split()
        username = ""
        # traverse in the list
        for i in range(len(l) - 1):
            s = l[i]
            # adds the capital first character
            username += (s[0].upper())
            # l[-1] gives last item of list l. We
        # use title to print first character in
        # capital.
        number = 0
        if GetLastIdStaff() > 0 and GetLastIdStaff() < 10:
            number = '{}{}'.format(1000, GetLastIdStaff())
        elif GetLastIdStaff() > 9 and GetLastIdStaff() < 100:
            number = '{}{}'.format(100, GetLastIdStaff())
        elif GetLastIdStaff() > 99 and GetLastIdStaff() < 1000:
            number = '{}{}'.format(10, GetLastIdStaff())
        elif GetLastIdStaff() > 999 and GetLastIdStaff() < 10000:
            number = '{}{}'.format(1, GetLastIdStaff())
        username += l[-1].title()
        # first_letter = full_name[0][0]
        # three_letters_surname = full_name[1][0:3]
        # number = '{:03d}'.format(random.randrange(10000, 19999))
        username = '{}{}'.format(username, number)
        return username
    else:
        return messages.warning(request, f'Please enter fullname')


# Courses
def GetCourses(id):
    return get_object_or_404(Courses, id=id)


def GetLessons(Id):
    return get_object_or_404(Lessons, id=Id)


def GetStatusAttendance(Name):
    return get_object_or_404(StatusAttendance, Status=Name)


def GetCodeForCourse(Course):
    code = remove_accents(Course.lower())
    if len(code) > 1:
        # splits the string into a list
        l = code.split()
        Code = ""
        # traverse in the list
        for i in range(len(l)):
            s = l[i]
            # adds the capital first character
            Code += (s[0].upper())
        Code += str(random.randrange(1000, 9999))
        return Code
    else:
        return messages.warning(f'Please enter course name')


# Classes
def GetClass(Name):
    return get_object_or_404(Classes, Name=Name)


def GetCoursesWithId(id):
    return get_object_or_404(Courses, id=id)


def GetLessonWithCourseId(Name, Course):
    return get_object_or_404(Lessons, Course=GetCoursesWithId(Course), Name=Name)


def GetLesson(Name, Course):
    return get_object_or_404(Lessons, Course=GetCourses(Course), Name=Name)


def CreateAttendaces(Class):
    list_form = []
    for course in GetClass(Class).classcourse_set.all():
        for lesson in GetCourses(course.Course.id).lessons_set.all():
            for student in GetClass(Class).students_set.all():
                form_a = Attendance(Lesson=GetLesson(lesson.Name, course.Course.id),
                                    Student=GetStudent(student.admin.username), ClassCourse=ClassCourse.objects.get(Class__Name=Class, Course__id=course.Course.id))
                list_form.append(form_a)
    for item in list_form:
        item.save()


def CreateAttendacesWithCourse(Class, courselist):
    list_form = []
    listcourse = []
    liststudent = []

    for item in Attendance.objects.filter(Student__Class__Name=Class):
        listcourse.append(item.Lesson.Course.id)
    for item in GetClass(Class).students_set.all():
        liststudent.append(item.admin.username)
    for course in courselist:
        if course not in listcourse:
            for lesson in GetCourses(course).lessons_set.all():
                for student in GetClass(Class).students_set.all():
                    form_a = Attendance(Lesson=GetLesson(lesson.Name, course),
                                        Student=GetStudent(
                                            student.admin.username),
                                        ClassCourse_id=ClassCourse.objects.get(Class__id=GetClass(Class).id, Course__id=course).id)
                    list_form.append(form_a)
    for item in list_form:
        item.save()


def CreateAttendacesWithStudents(Class, studentlist):
    list_form = []
    listcourse = []
    for item in ClassCourse.objects.filter(Class__Name=Class):
        listcourse.append(item.Course.id)
    for course in listcourse:
        for lesson in GetCourses(course).lessons_set.all():
            for student in studentlist:
                form_a = Attendance(Lesson=GetLesson(lesson.Name, course),
                                    Student=GetStudent(student),
                                    ClassCourse_id=ClassCourse.objects.get(Class__id=GetClass(Class).id, Course__id=course).id)
                list_form.append(form_a)
    for item in list_form:
        item.save()

def UpdateAttendance(Class, studentlist):
    classcourses = ClassCourse.objects.filter(Class__Name=Class)

    for i in range(0, len(classcourses)):
        classcourse = ClassCourse.objects.get(id=classcourses[i].id)
        attendances = classcourse.attendance_set.all().order_by('Lesson__Session')
        for j in range(0, len(attendances)):
            for k in studentlist:
                if k == attendances[j].Student.admin.username:
                    item = Attendance.objects.filter(Lesson__id=attendances[j].Lesson_id, ClassCourse_id=attendances[j].ClassCourse_id, ClassRoom__isnull=False, Slot__isnull=False)
                    if len(item) > 0:
                        attendance = Attendance.objects.get(id=attendances[j].id)
                        attendance.ClassRoom_id = item[0].ClassRoom_id
                        attendance.Slot_id = item[0].Slot_id
                        attendance.Date = item[0].Date
                        attendance.save()


def CreateAttendacesWithId(Students, Courses):
    list_form = []
    for course in Courses:
        for lesson in GetCoursesWithId(course).lessons_set.all():
            for student in Students:
                form_a = Attendance(Lesson=GetLessonWithCourseId(lesson, course), Student=GetStudent(student),
                                    ClassCourse_id=ClassCourse.objects.get(Class__id=GetStudent(student).Class_id, Course__id=GetCourses(course).id))
                list_form.append(form_a)
    for item in list_form:
        item.save()


def RemoveStudentInClass(liststudent):
    for student in liststudent:
        form = ClassStudent(instance=GetStudent(student))
        form = form.save(commit=False)
        form.Class = None
        form.save()


def RemoveCoursesInClass(Class, listcourse):
    for item in listcourse:
        ClassCourse.objects.get(Class__Name=Class, Course__id=item).delete()


def RemoveAttendanceWithCourse(Class, courselist):
    list_form = []
    for i in courselist:
        for lesson in GetCourses(i).lessons_set.all():
            for student in GetClass(Class).students_set.all():
                form_a = Attendance.objects.filter(Lesson_id=lesson.id,
                                                   Student_id=student.id,
                                                   ClassCourse__Class__Name=Class,
                                                   ClassCourse__Course__id= i)

                if form_a != None and form_a != "":
                    list_form.append(form_a)
    for item in list_form:
        item.delete()


def RemoveAttendanceWithStudent(Class, studentlist):
    list_form = []
    for course in GetClass(Class).classcourse_set.all():
        for lesson in GetCourses(course.Course.id).lessons_set.all():
            for student in studentlist:
                form_a = Attendance.objects.filter(Lesson=GetLesson(lesson.Name, course.Course.id),
                                                   Student=GetStudent(student)).first()
                if form_a != None and form_a != "":
                    list_form.append(form_a)
    for item in list_form:
        item.delete()


def CoursesNoneClass(Class, Faculty):
    ListCourse = []
    ListCourseInClass = []
    for item in Courses.objects.filter(faculty__id=Faculty.id):
        ListCourse.append({'id': item.id,
                           'Name': item.Name})

    for item in ClassCourse.objects.filter(Class__Name=Class):
        ListCourseInClass.append({'id': item.Course.id,
                                  'Name': item.Course.Name})

    ListCourseNotInClass = []

    for item in ListCourse:
        if item not in ListCourseInClass:
            ListCourseNotInClass.append(item)

    return ListCourseNotInClass
