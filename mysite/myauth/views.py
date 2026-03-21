from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView

from myauth.models import Profile


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm # Базовая форма, где есть проверка ввода пароля (два поля пароля)
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form) -> HttpResponse:
        # Стандартное поведение только создаёт запись в базе данных
        response = super().form_valid(form)

        # Создание нового профиля.
        Profile.objects.create(user=self.object)

        # Аутентификация по проверенным данным из формы
        username = form.cleaned_data.get('username') # Можно и через []
        password = form.cleaned_data.get('password1') # Два поля пароля для функционала "подтверждения"
        user = authenticate(self.request, username=username, password=password)

        # Авторизация. Пользователь точно существует, так как пользователь только что создан.
        # self.objet == user. Можно использовать оба варианта.
        login(self.request, user)

        return response


# В Django 5+ убрана работа LogoutView через http-метод GET.
# Основной предлагаемый вариант реализации - POST в форме. Но в данном случае форма не предполагалась.
# GET можно реализовать на View с переопределённым GET. Можно и переопределить его наследника - LogoutView.
# Но у LogoutView меньше разрешённых http-методов. Надо предварительно расширить http_method_names, добавив туда GET.
# Для теста (не из задания). LoginRequiredMixin - проверка аутентификацию. Направит на LOGIN_URL, если не аутентифицирован.
# Сделан для примера функционала. Практического смысла нет. LoginRequiredMixin должен быть первым.
class MyLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')


class UsersListView(ListView):
    # Оставлено стандартные названия параметров с суффиксом "_list": context_object_name = 'object_list'

    queryset = User.objects.select_related('profile')
    template_name = 'myauth/user_list.html' # Указано вручную, иначе искать будет в типовом auth, где находится User


class UserDetailView(DetailView):
    model = User
    template_name = 'myauth/user_detail.html' # Указано вручную, иначе искать будет в типовом auth, где находится User


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    # Для template использовано названия с типовым суффиксом "_form" - "profile_form.html".
    # Для удобства его решено заменить на "profile_update.html".
    template_name_suffix = '_update'

    model = Profile
    fields = 'bio', 'agreement_accepted', 'avatar'

    def test_func(self):
        # self.object вызывает ошибку:
        # 'ProfileUpdateView' object has no attribute 'object'
        # Поэтому приходится запрашивать отдельно - self.get_object(). Отдельный запрос к базе данных.
        profile: Profile = self.get_object()

        # Сохраняем объект в self.object ПЕРВЫМ ДЕЛОМ, чтобы запрос к базе данных был только один
        self.object = profile

        user = self.request.user

        # Это "администратор" со служебными правами
        if user.is_staff:
            return True

        # Текущий пользователь - владелец профиля
        return user == profile.user

    def get_success_url(self):
        user: User = self.object.user

        # Если просматривал самого себя, то можно вернуться на "About me".
        # На ней для текущего пользователя больше функционала.
        if self.request.user == user:
            return reverse('myauth:about-me')

        return reverse(
            'myauth:user_detail',
            kwargs={
                'pk': user.pk
            }
        )


def get_cookie(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('my_cookie', '<i>no cookie value</i>')
    return HttpResponse(f'Cookie value: {value!r}')


# Для теста (не из задания). user_passes_test - проверка наличия прав у пользователя.
# В отличие от permission_required, нет параметра raise_exception.
# Для обхода перенаправления можно перенести проверку прав в саму функцию. Вручную возвращать ответ с кодом 403.
@user_passes_test(lambda u: u.is_superuser)
def set_cookie(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set!')
    response.set_cookie('my_cookie', 'top secret cookie', max_age=3600) # Время жизни 1 ч.
    return response


@login_required # Для теста (не из задания). Проверка аутентификацию. Направит на LOGIN_URL, если не аутентифицирован.
def get_session(request: HttpRequest) -> HttpResponse:
    value = request.session.get('my_session', '<i>no session value</i>')
    return HttpResponse(f'Session value: {value!r}')


# Для теста (не из задания). permission_required - проверка наличия права просмотра профиля.
# raise_exception=True - для исправления бесконечного перенаправления "ERR_TOO_MANY_REDIRECTS" на страницу LOGIN_URL.
@permission_required('myauth.view_profile', raise_exception=True)
def set_session(request: HttpRequest) -> HttpResponse:
    request.session['my_session'] ='top secret session'
    return HttpResponse('Session set!')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
