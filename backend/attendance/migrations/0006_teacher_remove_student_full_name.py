# Generated by Django 5.1.1 on 2024-09-18 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0005_alter_student_student_class"),
    ]

    operations = [
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
        ),
        migrations.RemoveField(
            model_name="student",
            name="full_name",
        ),
    ]
