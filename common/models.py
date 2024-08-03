from django.db import models


class BlackListSection(models.Model):
    u"""
    블랙 리스트 섹션
    """
    name = models.CharField(max_length=45, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '블랙리스트 섹션'
        verbose_name_plural = '블랙리스트 섹션'


class BlackListWord(models.Model):
    u"""
    블랙 리스트 문구
    """
    wording = models.TextField(blank=True, null=True)
    black_list_section = models.ForeignKey(
        BlackListSection,
        models.DO_NOTHING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '블랙리스트 문구'
        verbose_name_plural = '블랙리스트 문구'
