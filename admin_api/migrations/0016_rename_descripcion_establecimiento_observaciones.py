# Generated by Django 4.2.1 on 2023-05-27 05:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0015_rename_observaciones_establecimiento_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='establecimiento',
            old_name='descripcion',
            new_name='observaciones',
        ),
    ]
