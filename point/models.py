from django.db import models
from member.models import Guest
from point.consts import PointType


class GuestPoint(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.DO_NOTHING)
    type = models.CharField(
        max_length=255,
        default=PointType.NORMAL_POINT.value,
        db_index=True,
        choices=PointType.choices(),
    )
    point = models.BigIntegerField(db_index=True)
    reason = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, db_index=True)
    valid_until = models.DateTimeField(null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Guest 포인트'
        verbose_name_plural = 'Guest 포인트'

    def __str__(self):
        return f'{self.guest} - {self.point} - is_active: {self.is_active}'
