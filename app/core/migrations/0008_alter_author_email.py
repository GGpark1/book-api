# Generated by Django 4.1.7 on 2023-02-16 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_author_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='email',
            field=models.EmailField(default=None, max_length=255),
        ),
    ]