from django.contrib import admin
from django.urls import path
from polls import views
from django.contrib.auth import views as auth_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name='polls'),
    path("SignUp/", views.signup, name='signup'),
    path("search_results/", views.results, name='search_results'),
    path("profile/", views.profile, name='profile'),
    path("NewUser/", views.new_user, name='newuser'),
    path("<int:movie_id>/", views.movie_details, name="moviedetail"),
    path("<int:movie_id>/rating/", views.rating, name='rating'),
    path("submit_review/<int:movie_id>/", views.submit_review, name='submit_review'),
    path("SignIn/", auth_view.LoginView.as_view(template_name='SignIn.html'), name='signin'),
    path("SignOut/", auth_view.LogoutView.as_view(template_name='SignOut.html'), name='signout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)