from django.contrib.auth.views import LoginView
from django.urls import path

from myauth.views import (
    MyLogoutView,
    get_cookie,
    get_session,
    set_cookie,
    set_session,
    AboutMeView,
    RegisterView,
    FooBarView,
    UsersListView,
    ProfileUpdateView,
    UserDetailView,
)

app_name = 'myauth'

urlpatterns = [
    path(
        'login/',
         LoginView.as_view(
             template_name='myauth/login.html',
             redirect_authenticated_user=True, # Если аутентифицирован, то сразу перенаправлять на LOGIN_REDIRECT_URL
         ),
         name='login'
    ),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('about-me/', AboutMeView.as_view(), name="about-me"),
    path('register/', RegisterView.as_view(), name="register"),
    path('users/', UsersListView.as_view(), name='user_list'),
    path('users/<int:pk>/update/', ProfileUpdateView.as_view(), name='user_update'),
    path("users/<int:pk>/", UserDetailView.as_view(), name='user_detail'),

    path('cookie/get/', get_cookie, name='cookie-get'),
    path('cookie/set/', set_cookie, name='cookie-set'),
    path('session/get/', get_session, name='session-get'),
    path('session/set/', set_session, name='session-set'),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"), # Из видео курса
]