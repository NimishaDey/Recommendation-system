from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# Create your models here.
class Movie(models.Model):
    title=models.CharField(max_length=300)
    genres=models.CharField(max_length=200)
    def __str__(self):
        return str(self.pk)


class Ratings(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=None)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE,default=None)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField(default=0.0, blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

