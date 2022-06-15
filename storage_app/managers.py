from django.db import models


class StorageQuerySet(models.QuerySet):

    def count_min_box_price(self):
        min_box_price = self.boxes.aggregate(models.Min('month_rent_price'))['month_rent_price__min']

        return min_box_price

    def count_squares_meters(self):
        squares_meters_count = self.boxes.aggregate(models.Sum('size'))['size__sum']

        return squares_meters_count

    def count_free_squares_meters(self):
        rented_squares_meters_count = self.boxes.filter(is_rented=True).aggregate(models.Sum('size'))['size__sum']
        free_squares_meters_count = self.count_squares_meters() - rented_squares_meters_count

        return free_squares_meters_count

    def count_free_boxes(self):
        free_boxes_count = self.boxes.count() - self.boxes.filter(is_rented=True).count()

        return free_boxes_count


class BoxQuerySet(models.QuerySet):
    pass


class BoxOrderQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for box_order in self:
            box_order.box.is_rented = False
            box_order.box.save(*args, **kwargs)

        super().delete(*args, **kwargs)
