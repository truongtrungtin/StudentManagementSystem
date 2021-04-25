from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "App.AdminView":
                    pass
                elif modulename == "App.views" or modulename == "django.views.static":
                    pass
                elif modulename == "django.contrib.auth.views" or modulename == "django.contrib.admin.sites":
                    pass
                else:
                    return HttpResponseRedirect(reverse("AdminPage"))
            elif user.user_type == "2":
                if modulename == "App.StaffView" or modulename == "App.EditResultVIewClass":
                    pass
                elif modulename == "App.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("StaffPage"))
            elif user.user_type == "3":
                if modulename == "App.TrainerView" or modulename == "django.views.static":
                    pass
                elif modulename == "App.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("TrainerPage"))
            elif user.user_type == "4":
                if modulename == "App.StudentView" or modulename == "django.views.static":
                    pass
                elif modulename == "App.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("StudentPage"))
            else:
                return HttpResponseRedirect(reverse("Login"))
        else:
            if request.path == reverse("ShowLogin") or request.path == reverse("DoLogin") or modulename == "django.contrib.auth.views" or modulename == "App.views" or modulename == "django.contrib.admin.sites":
                pass
            else:
                return HttpResponseRedirect(reverse("ShowLogin"))
