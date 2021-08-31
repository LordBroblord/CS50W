# Generated by Django 3.2.6 on 2021-08-26 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210826_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('', ''), ('IT', 'Items'), ('PB', 'Poké Balls'), ('ME', 'Medicine'), ('TM', 'TMs & HMs'), ('BE', 'Berries'), ('KI', 'Key Items')], default='', max_length=2),
        ),
    ]
