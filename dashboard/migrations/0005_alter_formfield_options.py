# Generated by Django 4.2.20 on 2025-03-30 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_companytheme'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formfield',
            options={'ordering': ['group__order', 'group', 'order'], 'verbose_name': 'Campo de formulario', 'verbose_name_plural': 'Campos de formulario'},
        ),
    ]
