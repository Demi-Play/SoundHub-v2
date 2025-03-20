from django import template

register = template.Library()

@register.filter(name='get_range')
def get_range(value):
    """
    Фильтр для создания диапазона чисел.
    Используется для отображения звезд рейтинга.
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0) 