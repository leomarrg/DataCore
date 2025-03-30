# Guardar como dashboard/migrations/0003_formfieldgroup_formfield_group.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_customform_formfield_formdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormFieldGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del grupo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('is_collapsed', models.BooleanField(default=True, verbose_name='Mostrar colapsado por defecto')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_groups', to='dashboard.customform')),
            ],
            options={
                'verbose_name': 'Grupo de campos',
                'verbose_name_plural': 'Grupos de campos',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='formfield',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fields', to='dashboard.formfieldgroup', verbose_name='Grupo de campos'),
        ),
    ]