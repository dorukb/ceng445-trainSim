# Generated by Django 2.2.12 on 2022-01-21 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('gridname', models.CharField(max_length=20, primary_key=b'I01\n', serialize=False)),
                ('data', models.BinaryField(max_length=2048)),
                ('UserIDList', models.BinaryField(max_length=1024)),
                ('author', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AttachedGrid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachedgrid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainSim.Grid')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
