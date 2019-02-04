# Generated by Django 2.1.4 on 2019-01-29 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0003_auto_20190123_1658'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='food_opted',
            new_name='food_option',
        ),
        migrations.AlterField(
            model_name='guest',
            name='current_city',
            field=models.CharField(blank=True, default='', max_length=600),
        ),
        migrations.AlterField(
            model_name='guest',
            name='current_country',
            field=models.ForeignKey(default='IND', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_addr_country', to='guesthouse.Country'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='current_state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_addr_state', to='guesthouse.State'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='occupation',
            field=models.CharField(choices=[('SR', 'Working'), ('ST', 'Studying')], default='ST', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='permanent_address_1',
            field=models.CharField(blank=True, default='', max_length=600),
        ),
        migrations.AlterField(
            model_name='guest',
            name='permanent_city',
            field=models.CharField(blank=True, default='', max_length=600),
        ),
        migrations.AlterField(
            model_name='guest',
            name='permanent_country',
            field=models.ForeignKey(default='IND', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='permanent_addr_country', to='guesthouse.Country'),
        ),
        migrations.AlterField(
            model_name='guest',
            name='permanent_state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='permanent_addr_state', to='guesthouse.State'),
        ),
    ]
