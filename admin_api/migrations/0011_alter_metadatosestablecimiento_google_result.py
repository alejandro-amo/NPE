# Generated by Django 4.2.1 on 2023-05-22 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0010_rename_resultado_consulta_google_metadatosestablecimiento_google_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatosestablecimiento',
            name='google_result',
            field=models.TextField(blank=True, null=True),
        ),
    ]
