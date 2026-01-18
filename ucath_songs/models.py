from email.policy import default
from random import choice
from django.db import models
from django.contrib.auth.models import User
import secrets
import string

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
    season = models.CharField(choices=season_choices, default='pending_approval')
    mtn = models.BooleanField(default=False)
    mtn_number = models.CharField(max_length=256)
    youtube_link = models.CharField(max_length=256)
    status = models.CharField(choices=song_status)
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
    ms_version = models.CharField(max_length=256)
    
    
class MidiFile(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    midi_file = models.FileField(upload_to='midi_files/')
    midi_version = models.CharField(max_length=256)


class Mp3File(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    mp3_file = models.FileField(upload_to='mp3_files/')
    mp3_version = models.CharField(max_length=256)
