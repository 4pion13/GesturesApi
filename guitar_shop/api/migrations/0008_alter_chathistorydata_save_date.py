# Generated by Django 5.1.1 on 2024-10-11 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_chathistorydata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chathistorydata',
            name='save_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
