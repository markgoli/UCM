from calendar import c
from django.views.generic import TemplateView, View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import *
from .forms import *


class LandingView(TemplateView):
    template_name = 'd-board.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mass_parts'] = Song.mass_parts
        
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
        queryset = Song.objects.filter(status='published').order_by("-created_at")
        
        # Search
        q = self.request.GET.get('q')
        print(q)
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(composer__icontains=q) | Q(part_of_mass__icontains=q) | Q(season__icontains=q))
            
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
    model = Song
    template_name = 'song_detail.html'
    context_object_name = 'song'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetching all related instances
        context['sheets'] = self.object.musicsheet_set.all()
        context['midis'] = self.object.midifile_set.all()
        context['audios'] = self.object.mp3file_set.all()
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


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy('admin_arrivals')
    
    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        # Get the song title before it's deleted to use in the message
        song = self.get_object()
        messages.success(request, f"Manuscript '{song.title}' has been permanently purged from the registry.")
        return super().delete(request, *args, **kwargs)

class UserLoginView(LoginView):
    """User login view"""
    template_name = 'd-board.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username.upper()}! \n Cantus - UCM is here for you!.')
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


class AdminArrivalsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Song
    template_name = 'admin/admin_new_arrival.html'
    context_object_name = 'songs'
    
    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        query = self.request.GET.get('q')
        # Admins see all, but filtered by search if present
        queryset = Song.objects.all().order_by('status', '-created_at')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(composer__icontains=query)
            )
        return queryset

    def render_to_response(self, context, **response_kwargs):
        # If HTMX request, only render the grid part
        if self.request.headers.get('HX-Request'):
            # We use the same template but tell Django to only render the grid div
            # Or better yet, return a separate small template for the grid
            return self.render_to_response_partial(context)
        return super().render_to_response(context, **response_kwargs)

    def render_to_response_partial(self, context):
        # This renders just the grid part for HTMX
        # You can also use a small partial template like 'admin/partials/song_grid.html'
        self.template_name = 'admin/partials/song_grid.html' 
        return super().render_to_response(context)

class AdminSongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Song
    form_class = SongForm
    template_name = 'admin/admin_song_detail.html'
    
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # Fetch actual related objects for display in the right panel
        data['saved_sheets'] = self.object.musicsheet_set.all()
        data['saved_audios'] = self.object.mp3file_set.all()
        data['saved_midis'] = self.object.midifile_set.all()
        return data

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f"Manuscript '{self.object.title}' updated successfully.")
        return redirect('admin_song_detail', slug=self.object.slug)


# Add a specific delete view for assets to handle the trash icons
def delete_asset(request, asset_type, asset_id):
    if not request.user.is_staff:
        return redirect('login')
    
    if asset_type == 'sheet':
        asset = get_object_or_404(MusicSheet, id=asset_id)
    elif asset_type == 'audio':
        asset = get_object_or_404(Mp3File, id=asset_id)
    elif asset_type == 'midi':
        asset = get_object_or_404(MidiFile, id=asset_id)
        
    song_slug = asset.song.slug
    asset.delete()
    messages.info(request, "Asset removed from manuscript.")
    return redirect('admin_song_detail', slug=song_slug)


class AssetUploadBaseView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Base logic for staff-only asset uploads"""
    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self, slug):
        return reverse('admin_song_detail', kwargs={'slug': slug})

class UploadSheetView(AssetUploadBaseView):
    def post(self, request, slug):
        song = get_object_or_404(Song, slug=slug)
        file = request.FILES.get('file')
        version = request.POST.get('ms_version', 'Standard Folio')
        
        if file:
            MusicSheet.objects.create(song=song, music_sheet=file, ms_version=version)
            messages.success(request, "Folio manuscript added.")
        return redirect(self.get_success_url(slug))

class UploadAudioView(AssetUploadBaseView):
    def post(self, request, slug):
        song = get_object_or_404(Song, slug=slug)
        file = request.FILES.get('file')
        version = request.POST.get('mp3_version', 'Master Recording')
        
        if file:
            Mp3File.objects.create(song=song, mp3_file=file, mp3_version=version)
            messages.success(request, "Audio asset synced.")
        return redirect(self.get_success_url(slug))

class UploadMidiView(AssetUploadBaseView):
    def post(self, request, slug):
        song = get_object_or_404(Song, slug=slug)
        file = request.FILES.get('file')
        version = request.POST.get('midi_version', 'Synthesized Logic')
        
        if file:
            MidiFile.objects.create(song=song, midi_file=file, midi_version=version)
            messages.success(request, "Midi sequence added.")
        return redirect(self.get_success_url(slug))




