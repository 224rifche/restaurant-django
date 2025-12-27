from django.utils import timezone

from apps.payments.models import Caisse


def send_daily_cash_report():
    caisse = Caisse.get_derniere_caisse()
    _ = timezone.now()
    return caisse
