# Generated by Django 4.1.12 on 2025-03-26 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacion', '0003_department_parent_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='access_level',
            field=models.CharField(choices=[('gerencial', 'Gerencial'), ('admin', 'Administrador'), ('programatico', 'Programático'), ('user', 'Usuario Regular')], max_length=50),
        ),
    ]
