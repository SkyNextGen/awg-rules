"""Human-readable ages for source and snapshot diagnostics."""


class FreshnessError(ValueError):
    """A freshness failure with a message suitable for the public report."""


def format_age(age):
    days, minutes = divmod(int(age.total_seconds() // 60), 24 * 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if days:
        word = 'дней'
        if not 11 <= days % 100 <= 14:
            if days % 10 == 1:
                word = 'день'
            elif 2 <= days % 10 <= 4:
                word = 'дня'
        parts.append(f'{days} {word}')
    if hours:
        parts.append(f'{hours} ч')
    if minutes:
        parts.append(f'{minutes} мин')
    return ' '.join(parts) or 'меньше минуты'


def age_detail(age):
    if age.total_seconds() < 0:
        return f'Дата на {format_age(-age)} позже текущего времени.'
    return f'Возраст данных — {format_age(age)}.'
