# Generated by Django 3.1 on 2020-08-29 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('busker', '0003_auto_20200827_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadcode',
            name='last_used_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]