from django.contrib import admin
from django.urls import path, include
from App.views import logout_user, ShowLoginPage, DoLogin
from App import StaffView, TrainerView, StudentView, AdminView, views

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('Forgot-Password/', include([
        path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
        path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    ])),
    path('', ShowLoginPage, name="ShowLogin"),
    path('DoLogin/', DoLogin, name="DoLogin"),
    path('logout_user/', logout_user, name="logout_user"),
    # path('admin_home', Login, name="admin_home"),


    # StaffPage
    path('StaffPage/', include([
        path('', StaffView.StaffPage.as_view(), name="StaffPage"),
        # Profile
        path('Profile/', StaffView.StaffProfile.as_view(),
             name="StaffProfile"),
        # Manage Students
        path('Students/', include([
            path('', StaffView.ListViewAccountStudents.as_view(
            ), name='ListViewAccountStudents'),
            path('Edit/<str:Username>/', StaffView.UpdateAccountStudent.as_view(),
                 name='UpdateAccountStudent'),
            path('Detail/<str:Username>/', StaffView.DetailAccountStudent.as_view(),
                 name='DetailAccountStudent'),
            path('Create/', StaffView.CreateAccountStudent.as_view(),
                 name='CreateAccountStudent'),
        ])),
        # Manage Trainers
        path('Trainers/', include([
            path('', StaffView.ListViewAccountTrainers.as_view(
            ), name='ListViewAccountTrainers'),
            path('Edit/<str:Username>/', StaffView.UpdateAccountTrainer.as_view(),
                 name='UpdateAccountTrainer'),
            path('Detail/<str:Username>/', StaffView.DetailAccountTrainer.as_view(),
                 name='DetailAccountTrainer'),
            path('Create/', StaffView.CreateAccountTrainer.as_view(),
                 name='CreateAccountTrainer'),
        ])),
        # Manage Classes
        path('Classes/', include([
            path('', StaffView.ListViewClass.as_view(),
                                 name='ListViewClass'),
            path('<str:Name>/Update/',
                 StaffView.UpdateClass.as_view(), name='UpdateClass'),
            path('Create/', StaffView.CreateClass.as_view(),
                 name='CreateClass'),
            path('<str:Name>/Students/', StaffView.ViewStudentInClass.as_view(),
                 name='ViewStudentInClass'),
            path('<str:Class>/AddStudents/',
                 StaffView.AddStudentToClass.as_view(), name='AddStudentToClass'),
            # path('<str:Class>/<str:Username>/Update/', StaffView.UpdateStudentInClass.as_view(),
            #      name='UpdateStudentInClass'),
            path(
                '<str:Name>/Courses/', StaffView.ViewCourseInClass.as_view(), name='ViewCourseInClass'),
            path('<str:Class>/AddCourse/',
                 StaffView.AddCourseToClass.as_view(), name='AddCourseToClass'),
            path('<str:Class>/<uuid:Course>/Update/', StaffView.UpdateCourseInClass.as_view(),
                 name='UpdateCourseInClass'),
            path('<str:Class>/<uuid:Course>/Statistical/', StaffView.StatisticsOfCoursesInClass.as_view(),
                 name='StatisticsOfCoursesInClass'),
            path('<str:Class>/Course/<uuid:Course>/Schedule/', StaffView.ScheduleOfCoursesInClass.as_view(),
                 name='ScheduleOfCoursesInClass'),
        ])),
        # Manage Courses
        path('Courses/', include([
            path('', StaffView.ListViewCourse.as_view(),
                                 name='ListViewCourse'),
            path('Create/', StaffView.CreateCourse.as_view(),
                 name='CreateCourse'),
            path(
                '<uuid:id>/Update/', StaffView.UpdateCourse.as_view(), name='UpdateCourse'),
            path('<uuid:id>/', StaffView.DetailCourse.as_view(),
                 name='DetailCourse'),
        ])),
        path('Calendar/', include([
            path('', StaffView.Calendar.as_view(),
                 name='CalendarForStaff'),
            path(
                'Scheduleforclass/', StaffView.ScheduleForClass.as_view(), name='ScheduleForClass')

        ])),
    ])),
    path('AdminPage/', include([
        path('', AdminView.AdminPage.as_view(), name="AdminPage"),
        path('Staffs/', include([
            path('', AdminView.ListViewAccountStaff.as_view(),
                 name='ListViewAccountStaff'),
            path('Edit/<str:Username>/', AdminView.UpdateAccountStaff.as_view(),
                 name='UpdateAccountStaff'),
            path('Create/', AdminView.CreateAccountStaff.as_view(),
                 name='CreateAccountStaff'),
        ])),
        path('Profile/<str:Username>/',
             AdminView.AdminProfile.as_view(), name="AdminProfile"),
        path('Staffs/<str:Username>/', AdminView.Profile.as_view(),
             name="ProfileAccountStaffs"),
        path('Faculties/', include([
            path('', AdminView.ListViewFaculty.as_view(),
                 name='ListViewFaculty'),
            path('Create/', AdminView.CreateFaculty.as_view(),
                 name='CreateFaculty'),
            path(
                '<str:name>/Update/', AdminView.UpdateFaculty.as_view(), name='UpdateFaculty'),
        ])),
        path("Slots/", include([
            path('', AdminView.ListViewSlots.as_view(),
                 name='ListViewSlot'),
            path('Create/', AdminView.CreateSlots.as_view(),
                 name='CreateSlot'),
            path('<uuid:id>/Update/',
                 AdminView.UpdateSlots.as_view(), name='UpdateSlot'),
            path('<uuid:id>/Delete/',
                 AdminView.DeleteSlots.as_view(), name='DeleteSlot'),
        ])),
        path("ClassRoom/", include([
            path('', AdminView.ListViewClassRoom.as_view(),
                 name='ListViewClassRoom'),
            path('Create/', AdminView.CreateClassRoom.as_view(),
                 name='CreateClassRoom'),
            path(
                '<uuid:id>/Update/', AdminView.UpdateClassRoom.as_view(), name='UpdateClassRoom'),
            path(
                '<uuid:id>/Delete/', AdminView.DeleteClassRoom.as_view(), name='DeleteClassRoom'),
            path('Calendar/<uuid:id>', AdminView.Calendar.as_view(),
                 name='CalendarForClassRoom'),

        ])),
    ])),
    # TrainerPage
    path('TrainerPage/', include([
        path('', TrainerView.TrainerPage.as_view(),
             name="TrainerPage"),
        path('Attendance/<str:Class>/<uuid:Course>/<uuid:Lesson>',
             TrainerView.Attendances.as_view(), name='Attendances'),
        path('Profile', TrainerView.trainer_profile.as_view(),
             name="trainer_profile"),
        path('MyCourses/', include([
            path('',TrainerView.ViewMyCourses.as_view(),
                 name="TrainerViewCourses"),
            path('<uuid:Course>/',StudentView.student_view_attendance.as_view(), name="student_view_attendance")
        ])),
    ])),
    # StudentPage
    path('StudentPage/', include([
        path('', StudentView.StudentPage.as_view(),
             name="StudentPage"),
        path('MyCourses/', include([
            path('',StudentView.StudentViewCourses.as_view(),
             name="StudentViewCourses"),
            path('<uuid:Course>/',StudentView.student_view_attendance.as_view(), name="student_view_attendance")
        ])),
        path('Timetable', StudentView.StudentViewTimeTable.as_view(),
             name="StudentViewTimeTable"),
        path('Profile', StudentView.student_profile.as_view(),
             name="student_profile"),
    ])),
]
