from django import forms
from .models import Song, MusicSheet, MidiFile, Mp3File


class SongUploadForm(forms.ModelForm):
    """Form for uploading a song with optional music sheet and MIDI file"""
    
    # Song fields
    title = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter song title'
        }),
        required=True
    )
    
    composer = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter composer name'
        }),
        required=True
    )
    
    arranged_by = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter arranger name (optional)'
        }),
        required=False
    )
    
    part_of_mass = forms.ChoiceField(
        choices=Song.mass_parts,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    
    season = forms.ChoiceField(
        choices=Song.season_choices,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    
    mtn = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_mtn'
        })
    )
    
    mtn_number = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter MTN number',
            'id': 'id_mtn_number'
        }),
        required=False,
        help_text='Required if MTN is selected'
    )
    
    youtube_link = forms.URLField(
        max_length=256,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter YouTube link (optional)'
        }),
        required=False
    )
    
    # Music Sheet fields (optional)
    music_sheet = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg'
        }),
        required=False,
        help_text='Upload music sheet (PDF or image) - Optional'
    )
    
    ms_version = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Music sheet version (e.g., v1.0)'
        }),
        required=False
    )
    
    # MIDI File fields (optional)
    midi_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.mid,.midi'
        }),
        required=False,
        help_text='Upload MIDI file - Optional'
    )
    
    midi_version = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MIDI file version (e.g., v1.0)'
        }),
        required=False
    )
    
    # MP3 File fields (optional)
    mp3_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.mp3'
        }),
        required=False,
        help_text='Upload MP3 file - Optional'
    )
    
    mp3_version = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MP3 file version (e.g., v1.0)'
        }),
        required=False
    )
    
    class Meta:
        model = Song
        fields = [
            'title', 'composer', 'arranged_by', 'part_of_mass', 
            'season', 'mtn', 'mtn_number', 'youtube_link'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        mtn = cleaned_data.get('mtn')
        mtn_number = cleaned_data.get('mtn_number', '').strip()
        
        # If MTN is checked, mtn_number is required
        if mtn and not mtn_number:
            raise forms.ValidationError({
                'mtn_number': 'MTN number is required when MTN is selected.'
            })
        
        # Set empty string for mtn_number if MTN is not checked
        if not mtn:
            cleaned_data['mtn_number'] = ''
        
        # If music_sheet is provided, ms_version should be provided
        music_sheet = cleaned_data.get('music_sheet')
        ms_version = cleaned_data.get('ms_version', '').strip()
        if music_sheet and not ms_version:
            raise forms.ValidationError({
                'ms_version': 'Music sheet version is required when uploading a music sheet.'
            })
        
        # If midi_file is provided, midi_version should be provided
        midi_file = cleaned_data.get('midi_file')
        midi_version = cleaned_data.get('midi_version', '').strip()
        if midi_file and not midi_version:
            raise forms.ValidationError({
                'midi_version': 'MIDI version is required when uploading a MIDI file.'
            })
        
        # If mp3_file is provided, mp3_version should be provided
        mp3_file = cleaned_data.get('mp3_file')
        mp3_version = cleaned_data.get('mp3_version', '').strip()
        if mp3_file and not mp3_version:
            raise forms.ValidationError({
                'mp3_version': 'MP3 version is required when uploading an MP3 file.'
            })
        
        # Set default empty strings for optional fields if not provided
        if not cleaned_data.get('arranged_by'):
            cleaned_data['arranged_by'] = ''
        if not cleaned_data.get('youtube_link'):
            cleaned_data['youtube_link'] = ''
        
        return cleaned_data

