# Generated by Django 4.1.10 on 2024-08-03 11:27
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Rule of Detail Description')),
                ('displayable', models.BooleanField(default=False, verbose_name='Promotion Displayable')),
                ('display_start_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Display Start')),
                ('display_end_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Display End')),
                ('action_page', models.CharField(choices=[('_blank', 'New Page'), ('_self', 'Same Page')], max_length=100, null=True, verbose_name='Action Page')),
                ('target_pk', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Action for using pk')),
                ('target_type', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Action for using type')),
                ('external_target_url', models.TextField(blank=True, null=True, verbose_name='Action for using url')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '프로모션 기본 규칙',
                'verbose_name_plural': '프로모션 기본 규칙',
            },
        ),
        migrations.CreateModel(
            name='PromotionTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Promotion Tag Name')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '프로모션 Tag',
                'verbose_name_plural': '프로모션 Tag',
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Banner title')),
                ('title_font_color', models.CharField(blank=True, max_length=100, null=True, verbose_name='Banner title font color')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Banner description')),
                ('description_font_color', models.CharField(blank=True, max_length=100, null=True, verbose_name='Banner description font color')),
                ('background_color', models.CharField(blank=True, max_length=100, null=True, verbose_name='Banner background color')),
                ('big_image', models.TextField(blank=True, null=True, verbose_name='Banner big page for image')),
                ('middle_image', models.TextField(blank=True, null=True, verbose_name='Banner middle page for image')),
                ('small_image', models.TextField(blank=True, null=True, verbose_name='Banner small page for image')),
                ('target_layer', models.CharField(choices=[('HOME_TOP', '홈 상단')], max_length=100, null=True, verbose_name='Banner target')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('promotion_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='promotion.promotionrule')),
                ('tags', models.ManyToManyField(blank=True, to='promotion.promotiontag')),
            ],
            options={
                'verbose_name': '배너',
                'verbose_name_plural': '배너',
            },
        ),
    ]
