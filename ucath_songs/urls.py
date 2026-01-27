from django.urls import path
from .views import *

urlpatterns = [
    path('', LandingView.as_view(), name='dashboard'),
    path('about-cantus-ucm/', AboutUsView.as_view(), name='about'),
    path('music-scores/library/', SongLibraryListView.as_view(), name='song_library'),
    path('music-scores/<slug:slug>/details/', SongDetailView.as_view(), name='song_detail'),
    path('music-scores/upload/', SongCreateView.as_view(), name='upload_song'),
    path('music-scores/<slug:slug>/edit/', SongUpdateView.as_view(), name='song_edit'),\
    path('music-scores/<slug:slug>/delete/', SongDeleteView.as_view(), name='song_delete'),
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('archive/links/', SongIndexListView.as_view(), name='song_links'),
    path('archive/download/<int:sheet_id>/', download_sheet, name='download_sheet'),
    # admin 
    path('scores-catalog/vlists/', AdminArrivalsView.as_view(), name='admin_arrivals'),
    path('music-scores/<slug:slug>/update/', AdminSongUpdateView.as_view(), name='admin_song_detail'),
    path('music-scores/delete-asset/<str:asset_type>/<int:asset_id>/', delete_asset, name='delete_asset'),
    path('music-scores/song/<slug:slug>/upload-sheet/', UploadSheetView.as_view(), name='upload_sheet'),
    path('music-scores/song/<slug:slug>/upload-audio/', UploadAudioView.as_view(), name='upload_audio'),
    path('music-scores/song/<slug:slug>/upload-midi/', UploadMidiView.as_view(), name='upload_midi'),
]