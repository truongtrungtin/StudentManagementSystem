from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import _unicode_ci_compare
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from StudentManagementSystem import settings
from API.models import CustomUser, Students, ImageStudent, Trainers, Classes, Courses, Lessons, ClassCourse, \
    StatusAttendance, Attendance, Faculties, Slots, ClassRoom

UserModel = get_user_model()

class UserCreateForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    address = forms.CharField(required=False)
    faculty = forms.UUIDField(required=False)
    telephone = forms.CharField()
    birthday = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',), required=False
    )


class UploadAvatar(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'Avatar',
        ]

    Avatar = forms.ImageField(label='Image')


class UserUpdateForm(forms.Form):
    email = forms.EmailField()
    address = forms.CharField(required=False)
    telephone = forms.CharField()
    faculty = forms.UUIDField(required=False)
    birthday = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',), required=False
    )


class ChangePassword(forms.Form):
    oldpassword = forms.CharField(widget=forms.PasswordInput())
    newpassword = forms.CharField(widget=forms.PasswordInput())
    confirmpassword = forms.CharField(widget=forms.PasswordInput())


class StudentStatus(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'is_active'
        ]

    username = forms.CharField(
        widget=forms.TextInput())


class TrainerStatus(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'is_active'
        ]

    username = forms.CharField(
        widget=forms.TextInput())


class StaffStatus(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'is_active'
        ]

    username = forms.CharField(
        widget=forms.TextInput())


class ClassStudent(forms.ModelForm):
    class Meta:
        model = Students
        fields = [
            'Class'
        ]


class ImageForm(forms.ModelForm):
    Url = forms.ImageField(label='Image')

    class Meta:
        model = ImageStudent
        fields = ('Url', 'FaceId')


# Attendance

class StatusAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'Status',
        ]


# Classes
class ClassesForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = [
            'Name',
            'faculty',
            'IsActive'
        ]


class UploadClassesForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = [
            'Name',
            'IsActive'
        ]


class AddStudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = [
            'Class',
        ]
#
#
# class AddCoursesForm(forms.ModelForm):
#     class Meta:
#         model = ClassCourse
#         fields = [
#             'Class',
#             'Course',
#         ]


class AddCoursesForm(forms.Form):
    Class = forms.UUIDField()
    Course = forms.UUIDField()


class AddAttendace(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'Lesson',
            'Student',
            'Date'
        ]

    Date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',)
    )


class AddTrainerToClass(forms.ModelForm):
    class Meta:
        model = ClassCourse
        fields = [
            'Trainer'
        ]


class AttendanceForm(forms.Form):
    ClassRoom = forms.UUIDField(required=False)
    Slot = forms.UUIDField(required=False)
    Date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',), required=False
    )

# Courses


class CourseStatus(forms.ModelForm):
    class Meta:
        model = Courses
        fields = [
            'IsActive'
        ]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = [
            'Name',
            'Code',
            'faculty',
            'Descriptions'
        ]


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculties
        fields = [
            'Name',
            'Descriptions'
        ]

# class SlotsForm(forms.Form):
#     Slot = forms.CharField()
#     StartTime = forms.DateTimeField(
#         widget=forms.DateTimeInput(format='%H:%M:%S'),
#         input_formats=('%H:%M:%S',), required=False
#     )
#     EndTime = forms.DateTimeField(
#         widget=forms.DateTimeInput(format='%H:%M:%S'),
#         input_formats=('%H:%M:%S',), required=False
#     )


class SlotsForm(forms.ModelForm):
    class Meta:
        model = Slots
        fields = [
            'Slot', 'StartTime', 'EndTime'
        ]


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = [
            'Name'
        ]


class ScheduleForm(forms.Form):
    Class = forms.UUIDField(required=True)
    LessonsPerWeek = forms.IntegerField(required=True)
    startTime = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',), required=False
    )

class ScheduleForCourseForm(forms.Form):
    LessonsPerWeek = forms.IntegerField(required=True)
    startTime = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y'),
        input_formats=('%d/%m/%Y',), required=False
    )


class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    def send_mail(self, context):
        html_message = render_to_string(
            'MailPage/password_reset.html', context)
        plain_message = strip_tags(html_message)
        msg = EmailMultiAlternatives(
            'Verify Email', plain_message, settings.EMAIL_HOST_USER, [self.cleaned_data["email"]])
        msg.attach_alternative(html_message, "text/html")
        msg.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        return (
            u for u in active_users
            if u.has_usable_password() and
            _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(self, domain_override=None, use_https=False, token_generator=default_token_generator, request=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(context)


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
