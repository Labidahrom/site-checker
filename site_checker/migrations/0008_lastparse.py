# Generated by Django 4.2.2 on 2023-07-08 02:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('site_checker', '0007_alter_check_actual_response_by_http_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastParse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parse_data', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
