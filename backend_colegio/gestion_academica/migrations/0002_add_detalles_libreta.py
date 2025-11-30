"""
Generated migration to add the 'detalles' JSONField to Libreta.
This file was created manually to match the model change in `models.py`.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_academica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libreta',
            name='detalles',
            field=models.JSONField(default=dict, blank=True),
        ),
    ]
