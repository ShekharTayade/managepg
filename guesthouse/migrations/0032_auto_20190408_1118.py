# Generated by Django 2.1.4 on 2019-04-08 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0031_auto_20190404_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacate',
            name='room_alloc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Room_allocation'),
        ),
    ]
