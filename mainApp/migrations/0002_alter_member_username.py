# Generated by Django 3.2.7 on 2021-11-14 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]