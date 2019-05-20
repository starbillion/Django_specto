# Generated by Django 2.0.7 on 2018-11-04 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainsite', '0003_restrictedipdevice_who_did'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restrictedipdevice',
            name='blocked_by_admin',
            field=models.BooleanField(default=True, help_text='This field show IP or Device is blocked by admin', verbose_name='active'),
        ),
    ]
