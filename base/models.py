from django.db import models
from datetime import date

# Create your models here.

class Summary(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    img = models.ImageField(null=True, blank=True, upload_to="src/media")
    name = models.CharField(max_length=200, default="Имя")
    second = models.CharField(max_length=200, default="Фамилия")
    birth_date = models.DateField(default=date.today, blank=True)
    city = models.CharField(max_length=300, default="Липецк")

    def __str__(self):
        return "Имя: {0}. Профессия: {1}. Город: {2}".format(self.name, self.title, self.city)

    def __unicode__(self):
        return self.title

class Person(models.Model):
    name = models.CharField(max_length=200)
    second = models.CharField(max_length=200)
    birth_date = models.DateTimeField()
    city = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name