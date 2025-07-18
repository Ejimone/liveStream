# Generated by Django 5.2 on 2025-04-04 00:15

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom_integration', '0003_alter_assignment_options_alter_course_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='material',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='material',
            name='assignment',
        ),
        migrations.AlterModelOptions(
            name='assignment',
            options={},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={},
        ),
        migrations.RenameField(
            model_name='course',
            old_name='owner',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='assignment',
            name='classroom_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='classroom_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assignment',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('processing', 'Processing'), ('draft_ready', 'Draft Ready'), ('reviewing', 'Reviewing'), ('generating_pdf', 'Generating PDF'), ('uploading', 'Uploading'), ('submitted', 'Submitted'), ('error', 'Error')], default='new', max_length=50),
        ),
        migrations.CreateModel(
            name='AssignmentDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ai_generated_content', models.TextField(blank=True, null=True)),
                ('user_edited_content', models.TextField(blank=True, null=True)),
                ('final_content_for_submission', models.TextField(blank=True, null=True)),
                ('is_final', models.BooleanField(default=False)),
                ('submitted', models.BooleanField(default=False)),
                ('submission_timestamp', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='draft', to='classroom_integration.assignment')),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('material_type', models.CharField(choices=[('pdf', 'PDF'), ('doc', 'Document'), ('slide', 'Slide')], max_length=50)),
                ('download_link', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='classroom_integration.assignment')),
            ],
        ),
    ]
