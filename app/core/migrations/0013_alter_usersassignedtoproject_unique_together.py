# Generated by Django 3.2.7 on 2021-10-10 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20211009_2332'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usersassignedtoproject',
            unique_together={('user', 'project')},
        ),
    ]
