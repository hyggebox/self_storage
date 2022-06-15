from django.db import models


class BoxOrderQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for box_order in self:
            box_order.box.is_rented = False
            box_order.box.save(*args, **kwargs)

        super().delete(*args, **kwargs)
