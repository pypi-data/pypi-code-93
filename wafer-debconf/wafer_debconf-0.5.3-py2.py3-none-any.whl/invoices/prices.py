import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from invoices.models import Invoice, InvoiceLine
from register.dates import get_ranges_for_dates

DEBCONF_NAME = settings.DEBCONF_NAME
INVOICE_PREFIX = settings.INVOICE_PREFIX
PRICES = settings.PRICES


def meal_prices():
    """Return a dict of meal name: USD price"""
    return {name: meal['price']
            for name, meal in settings.PRICES['meal'].items()}


def meal_price_string():
    """Return a human-readable string of daily meal prices"""
    prices = meal_prices()
    s = ['{} {} USD'.format(meal.title(), prices[meal])
         for meal in ('breakfast', 'lunch', 'dinner')
         if meal in prices]
    return ', '.join(s) + '.'


def invoice_user(user, force=False, save=False):
    from bursary.models import Bursary

    attendee = user.attendee

    try:
        bursary = user.bursary
    except Bursary.DoesNotExist:
        bursary = Bursary()

    lines = []
    fee = PRICES['fee'][attendee.fee]
    if fee['price']:
        lines.append(InvoiceLine(
            reference='{}REG-{}'.format(INVOICE_PREFIX, attendee.fee.upper()),
            description='{} {} registration fee'.format(
                DEBCONF_NAME, fee['name']),
            unit_price=fee['price'],
            quantity=1,
        ))

    try:
        accomm = attendee.accomm
    except ObjectDoesNotExist:
        accomm = None

    if accomm and not bursary.potential_bursary('accommodation'):
        for line in invoice_accomm(accomm):
            lines.append(InvoiceLine(**line))

    try:
        food = attendee.food
    except ObjectDoesNotExist:
        food = None

    if food and not bursary.potential_bursary('food'):
        for line in invoice_food(food):
            lines.append(InvoiceLine(**line))

    for paid_invoice in user.invoices.filter(status='paid', compound=False):
        lines.append(InvoiceLine(
            reference='INV#{}'.format(paid_invoice.reference_number),
            description='Previous Payment Received',
            unit_price=-paid_invoice.total,
            quantity=1,
        ))

    invoice = Invoice(
        recipient=user,
        status='new',
        date=timezone.now(),
        invoiced_entity=attendee.invoiced_entity,
        billing_address=attendee.billing_address
    )

    # Only save invoices if non empty
    if save and lines:
        invoice.save()

    total = 0
    for i, line in enumerate(lines):
        line.line_order = i
        total += line.total
        if save:
            line.invoice_id = invoice.id
            line.save()

    return {
        'invoice': invoice,
        'lines': lines,
        'total': total,
        'total_local': total * settings.DEBCONF_LOCAL_CURRENCY_RATE,
    }


def invoice_food(food):
    """Generate one invoice line per meal type per consecutive stay"""
    from register.models.food import Meal

    for meal, meal_label in Meal.MEALS.items():
        dates = [entry.date for entry in food.meals.filter(meal=meal)
                 if not entry.conference_dinner]
        if not dates:
            continue

        ranges = get_ranges_for_dates(dates)
        for first, last in ranges:
            n_meals = (last - first).days + 1

            if first != last:
                dates = '{} to {}'.format(first, last)
            else:
                dates = str(first)

            yield {
                'reference': '{}{}'.format(INVOICE_PREFIX, meal.upper()),
                'description': '{} {} ({})'.format(
                    DEBCONF_NAME, meal_label, dates),
                'unit_price': PRICES['meal'][meal]['price'],
                'quantity': n_meals,
            }

    if food.meals.filter(meal='dinner',
                         date=settings.DEBCONF_CONFERENCE_DINNER_DAY):
        food_price = PRICES['meal']['conference_dinner']
        yield {
            'reference': '{}CONFDINNER'.format(INVOICE_PREFIX),
            'description': '{} {} ({})'.format(
                DEBCONF_NAME,
                food_price.get('name', 'Conference Dinner'),
                settings.DEBCONF_CONFERENCE_DINNER_DAY.isoformat()),
            'unit_price': food_price['price'],
            'quantity': 1,
        }


def invoice_accomm(accomm):
    """Generate one invoice line per consecutive stay"""
    stays = get_ranges_for_dates(
        night.date for night in accomm.nights.all()
    )
    accom_price = PRICES['accomm']

    for first_night, last_night in stays:
        last_morning = last_night + datetime.timedelta(days=1)
        num_nights = (last_morning - first_night).days
        dates = "evening of %s to morning of %s" % (first_night,
                                                    last_morning)
        yield {
            'reference': '{}ACCOMM'.format(INVOICE_PREFIX),
            'description': '{} {} ({})'.format(
                DEBCONF_NAME,
                accom_price.get('name', 'on-site accommodation'),
                dates),
            'unit_price': accom_price['price'],
            'quantity': num_nights,
        }
