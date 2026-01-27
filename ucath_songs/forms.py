from pickle import TRUE
from django import forms
from .models import Song, MusicSheet, MidiFile, Mp3File
from django.forms import inlineformset_factory


class SongUploadForm(forms.ModelForm):
    """Form for uploading a song with optional music sheet and MIDI file"""
    
    # Song fields
    title = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the Song title'
        }),
        required=True
    )
    
    composer = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter name of the Composer'
        }),
        required=True
    )
    
    arranged_by = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Arranger name (optional)'
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
    
    mto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_mto'
        })
    )
    
    mto_number = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter MTO number',
            'id': 'id_mto_number'
        }),
        required=False,
        help_text='Required if MTO is selected'
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
            'accept': '.pdf'
        }),
        required=True,
        help_text='Upload music sheet (PDF)'
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
    
    midi_link = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MIDI file link (e.g., https://...)'
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
            'season', 'mto', 'mto_number', 'youtube_link'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        mto = cleaned_data.get('mto')
        mto_number = cleaned_data.get('mto_number', '').strip()
        
        # If MTo is checked, mto_number is required
        if mto and not mto_number:
            raise forms.ValidationError({
                'mto_number': 'MTo number is required when MTo is selected.'
            })
        
        # Set empty string for mto_number if MTo is not checked
        if not mto:
            cleaned_data['mto_number'] = ''
        
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


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'composer', 'arranged_by', 'part_of_mass', 'season', 'status', 'mto', 'mto_number', 'youtube_link']
        
    def __init__(self, *args, **kwargs):
        super(SongForm, self).__init__(*args, **kwargs)
        
        # Define which fields should be optional
        optional_fields = ['arranged_by', 'mto_number', 'youtube_link', 'composer']
        
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False

        # Keep your professional styling here
        self.fields['title'].widget.attrs.update({
            'class': 'w-full px-0 py-4 font-medium text-2xl bg-transparent border-0 border-b-2 border-slate-200 rounded-none focus:border-indigo-600 outline-none transition-all text-slate-900',
            'placeholder': 'Enter manuscript title...'
        })
        
        self.fields['composer'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-indigo-500 outline-none transition-all text-sm'
        })

        self.fields['arranged_by'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-indigo-500 outline-none transition-all text-sm'
        })
        
        self.fields['youtube_link'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-indigo-500 outline-none transition-all text-sm font-mono',
            'placeholder': 'https://youtube.com/...'
        })

        self.fields['mto_number'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-indigo-500 outline-none transition-all text-sm'
        })

        # Apply basic rounded-xl styles to selectors
        select_classes = 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none transition-all'
        self.fields['season'].widget.attrs.update({'class': select_classes})
        self.fields['part_of_mass'].widget.attrs.update({'class': select_classes})
        self.fields['status'].widget.attrs.update({'class': select_classes + ' font-bold text-indigo-600'})
        self.fields['mto'].widget.attrs.update({'class': 'w-5 h-5 accent-indigo-600 rounded'})


# Inline formsets allow managing related files on the same page as the Song
SheetFormSet = inlineformset_factory(Song, MusicSheet, fields=['music_sheet', 'ms_version'], extra=1, can_delete=True)
Mp3FormSet = inlineformset_factory(Song, Mp3File, fields=['mp3_file', 'mp3_version'], extra=1, can_delete=True)
MidiFormSet = inlineformset_factory(Song, MidiFile, fields=['midi_file', 'midi_version'], extra=1, can_delete=True)
