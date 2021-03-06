# Generated by Django 2.1.4 on 2019-04-18 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0035_auto_20190415_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='occupancy_dashboard',
            name='tenure',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='vacate',
            name='room_alloc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Room_allocation'),
        ),
    ]
