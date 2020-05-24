# Generated by Django 3.0.6 on 2020-05-24 11:42

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shipment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='billing_details',
            field=jsonfield.fields.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='transport',
            field=jsonfield.fields.JSONField(null=True),
        ),
    ]