from django.db import models
from promotion.consts import (
    ActionPage,
    BannerTargetLayer,
)


class PromotionRule(models.Model):
    description = models.TextField(verbose_name='Rule of Detail Description')
    displayable = models.BooleanField(verbose_name='Promotion Displayable', default=False)
    display_start_time = models.DateTimeField(verbose_name='Display Start', null=True, blank=True, db_index=True)
    display_end_time = models.DateTimeField(verbose_name='Display End', null=True, blank=True, db_index=True)
    action_page = models.CharField(
        verbose_name='Action Page',
        max_length=100,
        choices=ActionPage.choices(),
        null=True,
    )
    target_pk = models.CharField(
        verbose_name='Action for using pk',
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    target_type = models.CharField(
        verbose_name='Action for using type',
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    external_target_url = models.TextField(
        verbose_name='Action for using url',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '프로모션 기본 규칙'
        verbose_name_plural = '프로모션 기본 규칙'

    def __str__(self):
        return self.description


class PromotionTag(models.Model):
    name = models.CharField(
        verbose_name='Promotion Tag Name',
        max_length=100,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '프로모션 Tag'
        verbose_name_plural = '프로모션 Tag'

    def __str__(self):
        return self.name


class Banner(models.Model):
    promotion_rule = models.ForeignKey(PromotionRule, on_delete=models.CASCADE)

    title = models.CharField(
        verbose_name='Banner title',
        max_length=100,
        null=True,
        blank=True
    )
    title_font_color = models.CharField(
        verbose_name='Banner title font color',
        max_length=100,
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name='Banner description',
        null=True,
        blank=True,
    )
    description_font_color = models.CharField(
        verbose_name='Banner description font color',
        max_length=100,
        null=True,
        blank=True,
    )
    background_color = models.CharField(
        verbose_name='Banner background color',
        max_length=100,
        null=True,
        blank=True,
    )
    big_image = models.TextField(
        verbose_name='Banner big page for image',
        blank=True,
        null=True,
    )
    middle_image = models.TextField(
        verbose_name='Banner middle page for image',
        blank=True,
        null=True,
    )
    small_image = models.TextField(
        verbose_name='Banner small page for image',
        blank=True,
        null=True,
    )
    target_layer = models.CharField(
        verbose_name='Banner target',
        max_length=100,
        choices=BannerTargetLayer.choices(),
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(PromotionTag, blank=True)

    class Meta:
        verbose_name = '배너'
        verbose_name_plural = '배너'

    def __str__(self):
        return self.title
