from django.views.generic import TemplateView, View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib import messages
from .models import Song, MusicSheet, MidiFile, Mp3File
from .forms import SongUploadForm


class LandingView(TemplateView):
    template_name = 'd-board.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context


class SongLibraryListView(ListView):
    model = Song
    context_object_name = 'songs'
    paginate_by = 12

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['partials/song_grid.html']
        return ['songs_listing.html']

    def get_queryset(self):
        queryset = Song.objects.filter(status='pending_approval').order_by("-created_at")
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(composer__icontains=q))
            
        # Filters
        seasons = self.request.GET.getlist('season')
        if seasons:
            queryset = queryset.filter(season__in=seasons)
            
        parts = self.request.GET.getlist('part')
        if parts:
            queryset = queryset.filter(part_of_mass__in=parts)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['season_choices'] = Song.season_choices
        context['mass_parts'] = Song.mass_parts
        return context



class SongCreateView(CreateView):
    """Create a new song (upload)"""
    model = Song
    form_class = SongUploadForm
    template_name = 'upload_songs.html'
    success_url = reverse_lazy('song_library')
    login_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # Set song status based on whether user is admin/staff
        if self.request.user.is_staff or self.request.user.is_superuser:
            form.instance.status = 'published'
        else:
            form.instance.status = 'pending_approval'
        
        # Save the song first
        response = super().form_valid(form)
        song = form.instance
        
        # Handle Music Sheet upload
        music_sheet = form.cleaned_data.get('music_sheet')
        ms_version = form.cleaned_data.get('ms_version')
        if music_sheet and ms_version:
            MusicSheet.objects.create(
                song=song,
                music_sheet=music_sheet,
                ms_version=ms_version
            )
        
        # Handle MIDI File upload
        midi_file = form.cleaned_data.get('midi_file')
        midi_version = form.cleaned_data.get('midi_version')
        if midi_file and midi_version:
            MidiFile.objects.create(
                song=song,
                midi_file=midi_file,
                midi_version=midi_version
            )
        
        # Handle MP3 File upload
        mp3_file = form.cleaned_data.get('mp3_file')
        mp3_version = form.cleaned_data.get('mp3_version')
        if mp3_file and mp3_version:
            Mp3File.objects.create(
                song=song,
                mp3_file=mp3_file,
                mp3_version=mp3_version
            )
        
        # Show appropriate message based on status
        if form.instance.status == 'published':
            messages.success(self.request, f'Song "{song.title}" uploaded and published successfully!')
        else:
            messages.success(self.request, f'Song "{song.title}" uploaded successfully! It will be reviewed before publication.')
        
        return response
    
    def form_invalid(self, form):
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Upload New Song'
        context['button_text'] = 'Upload Song'
        return context




class SongDetailView(DetailView):
    """Detailed view of a single song"""
    model = Song
    template_name = 'song_detail.html'
    context_object_name = 'song'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song = self.get_object()
        
        # Get all related files
        context['music_sheets'] = MusicSheet.objects.filter(song=song)
        context['midi_files'] = MidiFile.objects.filter(song=song)
        context['mp3_files'] = Mp3File.objects.filter(song=song)
        
        return context


class SongUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing song"""
    model = Song
    template_name = 'song_form.html'
    fields = [
        'title', 'composer', 'arranged_by', 'part_of_mass', 
        'season', 'mtn', 'mtn_number', 'youtube_link'
    ]
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')
    
    def get_success_url(self):
        return reverse_lazy('song_detail', kwargs={'slug': self.object.slug})
    
    def form_valid(self, form):
        messages.success(self.request, f'Song "{form.instance.title}" updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Song'
        context['button_text'] = 'Update Song'
        return context


class SongDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a song"""
    model = Song
    template_name = 'song_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')
    
    def delete(self, request, *args, **kwargs):
        song = self.get_object()
        messages.success(request, f'Song "{song.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============ AUTHENTICATION VIEWS ============
class UserLoginView(LoginView):
    """User login view"""
    template_name = 'd-board.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username.upper()}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Username or Password.')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """User logout view"""
    next_page = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(CreateView):
    """User registration view"""
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully! Please log in.')
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, ListView):
    """User profile showing their uploaded songs"""
    model = Song
    template_name = 'profile.html'
    context_object_name = 'user_songs'
    login_url = reverse_lazy('login')
    paginate_by = 10
    
    def get_queryset(self):
        # If you add a user field to Song model later, filter by user
        # For now, return all songs
        return Song.objects.all().order_by('-created_at')





