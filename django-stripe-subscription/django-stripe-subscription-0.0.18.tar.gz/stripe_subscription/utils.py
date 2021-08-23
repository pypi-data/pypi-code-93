import logging
from datetime import datetime, timedelta

from django.apps import apps
from django.conf import settings
from django.core import mail
from django.core import signing
from django.template.loader import render_to_string

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


logger = logging.getLogger(__name__)


def get_product(plan):
    """
    Returns stripe product id for given plan.
    :param plan: billing.models.Plan
    """

    if not plan.product_id:
        product = stripe.Product.create(
                name=plan.title)
        plan.product_id = product.id

    return plan.product_id


def create_price_on_stripe(plan):
    """
    Creates stripe.Price object via SDK.
    :param plan: billing.models.Plan
    """

    price = stripe.Price.create(
        unit_amount=int(plan.price * 100),
        currency="usd",
        product=get_product(plan),
        recurring={"interval": plan.recurring_interval})

    plan.price_id = price.id


def update_price_on_stripe(plan):
    """
    Removes stripe.Price object via SDK.
    :param plan: billing.models.Plan
    """
    stripe.Price.modify(
        plan.price_id,
        active=plan.published)


def get_trial_end(days=3):
    """
    Returns trial end timestamp.
    :param days: Trial period
    :returns int: Trial end timestamp
    """
    trial_end = datetime.now() + timedelta(days=days)
    return int(trial_end.timestamp())


def cancel_subscription_confirm_email(host, subscription):
    """
    Sends cancel subscription email for given host and subscription.
    :param host: Host name
    :param subscription: stripe_subscription.models.Subscription
    :returns bool: True if message sent successfully
    """
    try:
        sub = stripe.Subscription.retrieve(subscription.subscription_id)
        pm = stripe.PaymentMethod.retrieve(sub.default_payment_method)
    except Exception as e:
        logger.error('Faield to retrieve subscription form stripe API:\n%s', e)
        return False

    cfg = apps.get_app_config('stripe_subscription')
    connection = cfg.get_smtp_connection(host)

    with connection:
        signer = signing.Signer()
        email_template = cfg.get_template(host, 'cancel-email')
        html = render_to_string(email_template, {
            'host': host,
            'object': subscription,
            'subscription': sub,
            'payment_method': pm,
            'token': signer.sign_object({
                'id': subscription.id,
                'sub': sub.id,
            })
        })

        msg = mail.EmailMessage(
            'Cancel subscription',
            html,
            cfg.get_from_email(host),
            [pm.billing_details.email],
            connection=connection
        )
        msg.content_subtype = "html"
        
        try:
            msg.send()
        except Exception as e:
            logger.error('Faield to send email with error:\n%s', e)
            return False

        return True


def cancel_subscription(subscription):
    """
    Immediately cancels given subscription via Stripe API
    :param subscription: stripe_subscription.models.Subscription
    """

    try:
        stripe.Subscription.delete(subscription.subscription_id)
    except Exception as e:
        logger.error('Faield to send email with error:\n%s', e)
        return False

    subscription.is_active = False
    subscription.save()

    return True
