from django.apps import apps
from django.core import signing
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Plan, Subscription
from .forms import SubscribeForm, CancelSubscriptionForm
from stripe_subscription import utils


def session(request):
    """
    Returns current user session.
    """

    if request.user and request.user.is_authenticated:
        qs = Plan.objects.list_published()

        return JsonResponse({
            "status": "ok",
            "session": {
                "csrf_token": get_token(request),
                "user": request.user.email,
                "plans": [
                    {'id': p.id, 'title': p.title, 'price': p.price}
                    for p in qs
                ]
            }
        })

    return JsonResponse({"status": "error"}, status=400)


@login_required
def subscribe(request):
    """
    Creates new subscription for current user with payment token and plan.
    """

    if request.method == "POST":
        form = SubscribeForm(request.POST)

        if form.is_valid():
            token = form.cleaned_data['stripe_token']
            plan = form.cleaned_data['plan']
            quiz = form.cleaned_data['quiz']

            sub = Subscription.create_from_token(
                    token,
                    plan,
                    request.user,
                    quiz)

            if sub:
                return JsonResponse({
                    "status": "ok",
                    "deep_link": '%s&email=%s&user_ip=%s' % (
                        sub.deep_link,
                        request.user.email,
                        request.META['REMOTE_ADDR']
                    )
                })
        else:
            return JsonResponse(
                    {"status": "error", "errors": form.errors},
                    status=400)

    return JsonResponse({"status": "error"}, status=400)


@csrf_exempt
def cancel_subscription(request):
    """
    Sends confirmation email to cancel subscription.
    User email address retrieved from stripe Subscription payment method.
    :param request: Request object
    """

    form = CancelSubscriptionForm(request.POST)

    if not form.is_valid():
        data = {
            "status": "error",
            "errors": form.errors
        }
        return JsonResponse(data, status=400)

    try:
        obj = Subscription.objects.get(subscription_id=form.cleaned_data['subscription_id'])
        is_ok = utils.cancel_subscription_confirm_email(request.get_host(), obj)

        if is_ok:
            return JsonResponse({"status": "ok"})

    except Subscription.DoesNotExist:
        raise Http404

    return JsonResponse({"status": "error", "error": "Something went wrong"}, status=400)


def cancel_subscription_confirm(request, token):
    signer = signing.Signer()

    try:
        data = signer.unsign_object(token)
    except signing.BadSignature:
        raise Http404

    try:
        obj = Subscription.objects.get(pk=data['id'], is_active=True)
    except Subscription.DoesNotExist:
        raise Http404

    cfg = apps.get_app_config('stripe_subscription')
    template = cfg.get_template(request.get_host(), 'cancel-success')
    context = {
        'is_ok': utils.cancel_subscription(obj)
    }

    return render(request, template, context)
