# Generated by Django 5.1.7 on 2025-05-04 17:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counseling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateField(auto_now_add=True)),
                ('counseling_date', models.DateField()),
                ('counseling_time', models.TimeField()),
                ('counseling_type', models.CharField(choices=[('교수상담', '교수상담'), ('글쓰기상담', '글쓰기상담')], max_length=20)),
                ('counseling_category', models.CharField(choices=[('학업', '학업'), ('진로', '진로'), ('심리', '심리')], max_length=20)),
                ('status', models.CharField(choices=[('신청', '신청'), ('대기', '대기'), ('예약확정', '예약확정'), ('완료', '완료'), ('취소', '취소')], default='신청', max_length=10)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('request_content', models.TextField()),
                ('result_content', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(max_length=20)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counselings', to='students.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counselings', to='teachers.teacher')),
            ],
            options={
                'ordering': ['-counseling_date', '-counseling_time'],
            },
        ),
    ]
