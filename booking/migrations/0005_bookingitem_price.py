# Generated by Django 4.2.4 on 2023-08-10 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_bookingitem_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
