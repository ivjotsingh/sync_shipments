# Generated by Django 3.0.6 on 2020-05-25 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailer', '0002_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shop',
            old_name='access_token',
            new_name='stored_access_token',
        ),
        migrations.AddField(
            model_name='shop',
            name='access_token_ttl',
            field=models.DateTimeField(null=True),
        ),
    ]
