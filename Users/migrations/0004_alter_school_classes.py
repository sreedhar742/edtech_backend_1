# Generated by Django 5.1 on 2024-08-29 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_student_class_name'),
        ('myapp', '0003_alter_question_answers_ai_answer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='classes',
            field=models.ManyToManyField(to='myapp.classes'),
        ),
    ]
