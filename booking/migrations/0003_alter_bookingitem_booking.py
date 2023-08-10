# Generated by Django 4.2.4 on 2023-08-09 10:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_alter_bookingitem_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingitem',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', related_query_name='books', to='booking.booking'),
        ),
    ]