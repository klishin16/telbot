# Generated by Django 2.1 on 2019-06-18 02:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20190618_0252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summary',
            name='birth_date',
        ),
    ]
