# Generated by Django 4.1.6 on 2023-02-15 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_birth_alter_user_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='birth',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'Male'), (2, 'Female')], default=0),
        ),
    ]
