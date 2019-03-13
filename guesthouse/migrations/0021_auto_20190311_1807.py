# Generated by Django 2.1.4 on 2019-03-11 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guesthouse', '0020_guesthouse_logo_small'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bed_conversion',
            fields=[
                ('bed_id', models.AutoField(primary_key=True, serialize=False)),
                ('bed_name', models.CharField(max_length=100)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Floor')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('bill_number', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('bill_date', models.DateField()),
                ('bill_for_month', models.CharField(max_length=6)),
                ('bill_for', models.CharField(choices=[('Monthly Rent', 'Monthly Rent'), ('Advance Payment', 'Advance Payment'), ('Advance Rent Payment', 'Advance Rent Payment'), ('Food Service', 'Food Service'), ('Other Services', 'Other Services')], max_length=2)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Booking')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Guest')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('receipt_number', models.CharField(max_length=15)),
                ('receipt_date', models.DateField()),
                ('receipt_for', models.CharField(choices=[('Monthly Rent', 'Monthly Rent'), ('Advance Payment', 'Advance Payment'), ('Advance Rent Payment', 'Advance Rent Payment'), ('Food Service', 'Food Service'), ('Other Services', 'Other Services')], max_length=2)),
                ('receipt_for_month', models.CharField(max_length=6, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('mode_of_payment', models.CharField(choices=[('CS', 'CASH'), ('ON', 'ONLINE'), ('CH', 'Cheque'), ('DD', 'Demand Draft')], max_length=2)),
                ('payment_reference', models.CharField(blank=True, default='', max_length=100)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('bill', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Bill')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Booking')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Guest')),
            ],
        ),
        migrations.CreateModel(
            name='Room_conversion',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('room_name', models.CharField(max_length=100, unique=True)),
                ('available_from', models.DateField(null=True)),
                ('available_to', models.DateField(null=True)),
                ('rent_per_bed', models.DecimalField(decimal_places=2, max_digits=12)),
                ('max_beds', models.IntegerField()),
                ('advance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Block')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Floor')),
            ],
        ),
        migrations.CreateModel(
            name='Vacation_period',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Booking')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Guest')),
            ],
        ),
        migrations.RenameField(
            model_name='room',
            old_name='room_rent',
            new_name='rent_per_bed',
        ),
        migrations.AlterField(
            model_name='room_allocation',
            name='guest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='guesthouse.Guest'),
        ),
        migrations.AddField(
            model_name='bed_conversion',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='guesthouse.Room'),
        ),
    ]
