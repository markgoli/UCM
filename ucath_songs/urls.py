from django.urls import path
from .views import *

urlpatterns = [
    path('', LandingView.as_view(), name='dashboard'),
    path('music-scores/library/', SongLibraryListView.as_view(), name='song_library'),
    path('music-scores/<slug:slug>/details/', SongDetailView.as_view(), name='song_detail'),
    path('music-scores/upload/', SongCreateView.as_view(), name='upload_song'),
    path('music-scores/<slug:slug>/edit/', SongUpdateView.as_view(), name='song_edit'),
    path('music-scores/<slug:slug>/delete/', SongDeleteView.as_view(), name='song_delete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]