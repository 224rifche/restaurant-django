from decimal import Decimal

from django import template

register = template.Library()


@register.filter(name='gnf')
def gnf(value):
    try:
        if value is None:
            return "0 GNF"

        amount = Decimal(str(value))
        amount_int = int(amount.quantize(Decimal('1')))
        formatted = f"{amount_int:,}".replace(",", " ")
        return f"{formatted} GNF"
    except Exception:
        return f"{value} GNF"


@register.filter(name='mul')
def mul(value, arg):
    try:
        if value is None or arg is None:
            return Decimal('0')
        return Decimal(str(value)) * Decimal(str(arg))
    except Exception:
        return 0
