# Generated by Django 4.2.2 on 2023-07-01 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('site_checker', '0003_alter_check_has_expected_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='url_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='site_checker.url'),
        ),
    ]