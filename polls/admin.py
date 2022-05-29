from django.contrib import admin
from django.urls import path
from .models import Movie,Ratings, Profile
from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import csv

# Register your models here.

#Instead of uploading one movie at a time admin can upload a csv with a list of movies
class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

@admin.register(Movie)
class movieAdmin(admin.ModelAdmin):
    list_display=('id','title','genres')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload_csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")

            for x in csv_data:
                fields = x.split(",")
                created = Movie.objects.update_or_create(
                    title = fields[1],
                    genres = fields[2],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)



admin.site.register(Ratings)
admin.site.register(Profile)
