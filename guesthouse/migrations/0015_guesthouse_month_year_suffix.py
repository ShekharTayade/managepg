# Generated by Django 2.1.4 on 2019-02-04 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0014_auto_20190204_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='guesthouse',
            name='month_year_suffix',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
