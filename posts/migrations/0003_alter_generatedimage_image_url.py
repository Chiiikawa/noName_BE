# Generated by Django 4.2.7 on 2023-11-20 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_generatedimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatedimage',
            name='image_url',
            field=models.ImageField(upload_to='generated_images/'),
        ),
    ]