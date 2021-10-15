# Generated by Django 3.2.7 on 2021-10-14 21:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_remove_ticket_ticket_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_value', models.CharField(max_length=100)),
                ('new_value', models.CharField(max_length=100)),
                ('date_changed', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.ticket')),
            ],
        ),
    ]