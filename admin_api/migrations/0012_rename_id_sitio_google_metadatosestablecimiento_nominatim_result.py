# Generated by Django 4.2.1 on 2023-05-22 03:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0011_alter_metadatosestablecimiento_google_result'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metadatosestablecimiento',
            old_name='id_sitio_google',
            new_name='nominatim_result',
        ),
    ]
