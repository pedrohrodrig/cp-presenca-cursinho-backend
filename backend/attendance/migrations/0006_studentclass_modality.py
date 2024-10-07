# Generated by Django 5.0.6 on 2024-10-07 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0005_alter_student_student_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentclass",
            name="modality",
            field=models.CharField(choices=[("ON", "Online"), ("IN", "Presencial")], default="IN", max_length=2),
        ),
    ]
