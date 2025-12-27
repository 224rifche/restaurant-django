from django.db import models


class DummyDashboardModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'dashboard_dummy'
