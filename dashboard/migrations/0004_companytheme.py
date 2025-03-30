# Guardar como dashboard/migrations/0004_companytheme.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacion', '0004_alter_department_access_level'),
        ('dashboard', '0003_formfieldgroup_formfield_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('primary_color', models.CharField(default='#56b3c7', max_length=20, verbose_name='Color primario')),
                ('secondary_color', models.CharField(default='#8fc73e', max_length=20, verbose_name='Color secundario')),
                ('accent_color', models.CharField(default='#FF9613', max_length=20, verbose_name='Color de acento')),
                ('text_color', models.CharField(default='#333333', max_length=20, verbose_name='Color de texto principal')),
                ('light_text_color', models.CharField(default='#ffffff', max_length=20, verbose_name='Color de texto claro')),
                ('font_family', models.CharField(default="'Montserrat', sans-serif", max_length=100, verbose_name='Familia de fuentes')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/', verbose_name='Logo de la compañía')),
                ('logo_small', models.ImageField(blank=True, null=True, upload_to='company_logos/', verbose_name='Logo pequeño/icono')),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='company_backgrounds/', verbose_name='Imagen de fondo')),
                ('custom_css', models.TextField(blank=True, null=True, verbose_name='CSS personalizado')),
                ('custom_js', models.TextField(blank=True, null=True, verbose_name='JavaScript personalizado')),
                ('enabled', models.BooleanField(default=True, verbose_name='Tema habilitado')),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='theme', to='autenticacion.company')),
            ],
            options={
                'verbose_name': 'Tema de compañía',
                'verbose_name_plural': 'Temas de compañías',
            },
        ),
    ]