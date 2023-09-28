from django.db import models


class OrderDelivery(models.Model):
    # Relationship
    order_grouping = models.ForeignKey(to='order.Grouping',
                                       on_delete=models.CASCADE)
    delivery = models.ForeignKey(to='delivery.Delivery',
                                 on_delete=models.CASCADE)
    # Object tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_delivery'
