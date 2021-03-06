# Generated by Django 2.1.4 on 2019-02-12 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0016_auto_20190204_2231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food_price',
            fields=[
                ('type', models.CharField(choices=[('VEG', 'Vegetarian'), ('NOV-VEG', 'Non-Vegetarian')], default='VEG', max_length=7, primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='advance',
            field=models.DecimalField(decimal_places=2, default=20000, max_digits=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='max_beds',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='room_rent',
            field=models.DecimalField(decimal_places=2, default=7500, max_digits=12),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='food_preference',
            field=models.CharField(blank=True, choices=[('VEG', 'Vegetarian'), ('NOV-VEG', 'Non-Vegetarian')], default='VEG', max_length=7),
        ),
        migrations.AlterField(
            model_name='guest',
            name='company_country',
            field=models.ForeignKey(blank=True, default='IND', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='company_addr_country', to='guesthouse.Country'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='current_country',
            field=models.ForeignKey(blank=True, default='IND', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='current_addr_country', to='guesthouse.Country'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='permanent_country',
            field=models.ForeignKey(blank=True, default='IND', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='permanent_addr_country', to='guesthouse.Country'),
        ),
    ]
