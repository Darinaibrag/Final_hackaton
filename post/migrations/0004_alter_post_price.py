# Generated by Django 4.2.4 on 2023-08-08 10:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0003_alter_post_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="price",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
