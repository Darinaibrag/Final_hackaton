# Generated by Django 4.2.4 on 2023-08-08 10:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0002_post_availability"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=255),
        ),
    ]
