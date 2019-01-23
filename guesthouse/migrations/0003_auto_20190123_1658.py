# Generated by Django 2.1.4 on 2019-01-23 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0002_auto_20190122_1707'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('bed_id', models.AutoField(primary_key=True, serialize=False)),
                ('bed_name', models.CharField(max_length=100, unique=True)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('block_id', models.AutoField(primary_key=True, serialize=False)),
                ('block_name', models.CharField(max_length=100, unique=True)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('floor_id', models.AutoField(primary_key=True, serialize=False)),
                ('floor_name', models.CharField(max_length=100, unique=True)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('room_name', models.CharField(max_length=100, unique=True)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Floor')),
            ],
        ),
        migrations.CreateModel(
            name='room_allocation',
            fields=[
                ('alloc_id', models.AutoField(primary_key=True, serialize=False)),
                ('allocation_start_date', models.DateTimeField()),
                ('allocation_end_date', models.DateTimeField(null=True)),
                ('created_date', models.DateTimeField()),
                ('updated_date', models.DateTimeField(null=True)),
                ('bed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Bed')),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block')),
            ],
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='gh_id',
            new_name='guesthouse',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_address1',
            new_name='address1',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_address2',
            new_name='address2',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_city',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_country',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='support_phonenumber',
            new_name='fax_number',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_state',
            new_name='phone_number',
        ),
        migrations.RenameField(
            model_name='guesthouse',
            old_name='gh_zip',
            new_name='state',
        ),
        migrations.AddField(
            model_name='booking',
            name='created_date',
            field=models.DateTimeField(default='2019-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='guest',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Guest'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='updated_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='guest',
            name='created_date',
            field=models.DateTimeField(default='2019-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='guest',
            name='id_card_number',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='guest',
            name='referred_by',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='guest',
            name='referred_by_contact_details',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='guest',
            name='updated_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='guesthouse',
            name='email_id',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='guesthouse',
            name='support_phone_number',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='guesthouse',
            name='zip',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='guest',
            name='company_contact_number',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='guest',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='room_allocation',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Booking'),
        ),
        migrations.AddField(
            model_name='room_allocation',
            name='floor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Floor'),
        ),
        migrations.AddField(
            model_name='room_allocation',
            name='guest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Guest'),
        ),
        migrations.AddField(
            model_name='room_allocation',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Room'),
        ),
        migrations.AddField(
            model_name='block',
            name='guesthouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Guesthouse'),
        ),
        migrations.AddField(
            model_name='bed',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block'),
        ),
        migrations.AddField(
            model_name='bed',
            name='floor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Floor'),
        ),
        migrations.AddField(
            model_name='bed',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Room'),
        ),
    ]
