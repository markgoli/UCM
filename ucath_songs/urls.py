from django.urls import path
from .views import *

urlpatterns = [
    path('', LandingView.as_view(), name='dashboard'),
    path('song/<slug:slug>/', SongDetailView.as_view(), name='song_detail'),
    path('songs/create/', SongCreateView.as_view(), name='upload_song'),
    path('song/<slug:slug>/edit/', SongUpdateView.as_view(), name='song_edit'),
    path('song/<slug:slug>/delete/', SongDeleteView.as_view(), name='song_delete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]