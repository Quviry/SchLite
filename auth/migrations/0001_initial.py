# Generated by Django 3.1.4 on 2021-01-31 13:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(auto_created=True, default=uuid.uuid4, unique=True)),
                ('login', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('dairy_cookie', models.CharField(max_length=400)),
                ('connector', models.CharField(max_length=128)),
                ('is_parent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Visits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('requested', models.CharField(max_length=200)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
    ]