# Generated by Django 2.1.4 on 2019-02-28 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0019_guesthouse_logo_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='guesthouse',
            name='logo_small',
            field=models.ImageField(null=True, upload_to='logo/'),
        ),
    ]
