# Generated by Django 4.2.1 on 2023-05-26 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0014_alter_establecimiento_fecha_actualizacion_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='establecimiento',
            old_name='observaciones',
            new_name='email',
        ),
    ]
