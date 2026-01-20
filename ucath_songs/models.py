from enum import unique
from random import choice
from django.db import models
from django.contrib.auth.models import User
import secrets
import string
import fitz 
import os
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

# Create your models here.

class Song(models.Model):

    season_choices = [
        ('lent', 'Lent'),
        ('easter', 'Easter'),
        ('christmas', 'Christmas'), 
        ('advent', 'Advent'), 
        ('ordinary', 'Ordinary Time'),
    ]

    mass_parts = [
        ('entrance', 'Entrance Procession'),
        ('penitential', 'Penitential Act / Kyrie'),
        ('gloria', 'Gloria'),
        ('collect', 'Collect'),
        ('responsorial', 'Responsorial Psalm'),
        ('meditation', 'Meditation'),
        ('gospel', 'Gospel Acclamation'),
        ('creed', 'Creed'),
        ('prayers', 'Prayers of the Faithful'),
        ('offertory', 'Offertory'),
        ('our_father', "Lord's Prayer"),
        ('sign_of_peace', 'Sign of Peace'),
        ('communion', 'Eucharist'),
        ('blessing', 'Blessing'),
        ('dismissal', 'Dismissal / Recession'),
        ('others', 'Others')
    ]

    song_status = [
        ('pending_approval', 'Pending Approval'),
        ('published', 'Published')
    ]

    title = models.CharField(max_length=256)
    composer = models.CharField(max_length=256)
    arranged_by = models.CharField(max_length=256)
    part_of_mass = models.CharField(choices=mass_parts)
    season = models.CharField(choices=season_choices, default='ordinary')
    mto = models.BooleanField(default=False)
    mto_number = models.CharField(max_length=256)
    youtube_link = models.CharField(max_length=256)
    status = models.CharField(choices=song_status, default='pending_approval')
    slug = models.SlugField(max_length=220, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]


    def generate_slug(self):
        """Generate a unique 16-character slug"""
        while True:
            # Generate 16 character alphanumeric string (uppercase)
            slug = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))

            if not Song.objects.filter(slug=slug).exists():
                return slug
    
    def save(self, *args, **kwargs):
        # Generate slug if not set
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)



    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} by {self.composer}"
    


class MusicSheet(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    music_sheet = models.FileField(upload_to='music_sheets/')
    thumbnail = models.ImageField(upload_to='music_thumbnails/', null=True, blank=True)
    ms_version = models.CharField(max_length=256, null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Save the file first
        super().save(*args, **kwargs)
        
        # 2. Generate thumbnail if missing
        if self.music_sheet and not self.thumbnail:
            self.generate_thumbnail_pure_python()

    def generate_thumbnail_pure_python(self):
        try:
            # Open the PDF directly from the file path
            doc = fitz.open(self.music_sheet.path)
            
            # Load the first page (0-indexed)
            page = doc.load_page(0)
            
            # Create a 'pixmap' (image) of the page
            # We use a matrix to increase resolution (2.0 = 2x zoom for clarity)
            zoom = 2.0 
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image to handle the JPEG conversion easily
            img_data = pix.tobytes("jpg")
            img = Image.open(BytesIO(img_data))
            
            # Save to buffer
            temp_thumb = BytesIO()
            img.save(temp_thumb, format='JPEG', quality=85)
            temp_thumb.seek(0)
            
            # Naming
            thumb_name = os.path.basename(self.music_sheet.name).rsplit('.', 1)[0] + '_thumb.jpg'
            
            # Save to field
            self.thumbnail.save(thumb_name, ContentFile(temp_thumb.read()), save=False)
            super().save(update_fields=['thumbnail'])
            
            doc.close()
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")


    def __str__(self) -> str:  # pragma: no cover
        return f"Music sheet for {self.song} - {self.ms_version}"
    
    
class MidiFile(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    midi_file = models.FileField(upload_to='midi_files/')
    midi_version = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"MIDI File for {self.song} - {self.midi_version}"


class Mp3File(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    mp3_file = models.FileField(upload_to='mp3_files/')
    mp3_version = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Mp3 File for {self.song} - {self.mp3_version}"
