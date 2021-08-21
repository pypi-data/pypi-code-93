from django.test import Client
from minidebconf.models import Registration
from minidebconf.models import get_user_model
from minidebconf.forms import RegisterForm
from wafer.schedule.models import ScheduleBlock
from pytest import fixture


User = get_user_model()


@fixture
def user(db):
    return User.objects.create(
        username="theuser",
        first_name="Firstname",
        last_name="Lastname",
    )


@fixture
def client(db, user):
    _client = Client()
    _client.force_login(user)
    return _client


@fixture
def days(db):
    day1 = ScheduleBlock.objects.create(start_time='2020-06-01 09:00+00', end_time='2020-06-01 18:00+00')
    day2 = ScheduleBlock.objects.create(start_time='2020-06-02 09:00+00', end_time='2020-06-02 18:00+00')
    day3 = ScheduleBlock.objects.create(start_time='2020-06-03 09:00+00', end_time='2020-06-03 18:00+00')
    return [day1, day2, day3]



class TestRegistrationModel:

    def test_full_name(self, user):
        registration = Registration(user=user)
        assert registration.full_name == "Firstname Lastname"


class TestRegistrationForm:

    def test_basics(self, user, days):
        form = RegisterForm(
            instance=Registration(user=user),
            initial={"days": days}
        )
        assert not form.errors

    def test_get_full_name_from_user(self, user, days):
        registration = Registration.objects.create(user=user, country="BR")
        registration.days.add(days[0])
        form = RegisterForm(instance=registration)
        assert form.fields['full_name'].initial == registration.full_name

    def test_pass_full_name_on_to_user(self, user, days):
        form = RegisterForm(
            instance=Registration(user=user),
            data={"days": days, "country": "BR", "full_name": 'Foo Bar'},
        )
        assert not form.errors
        form.save()
        user.refresh_from_db()
        assert user.first_name == "Foo"
        assert user.last_name == "Bar"


class TestRegistrationView:
    def test_register(self, user, client, days):
        response = client.post(
            '/register/',
            {
                "days": [days[1].id, days[2].id],
                "country": "BR",
                "full_name": "Foo Bar",
            }
        )
        assert response.status_code == 302
        registration = Registration.objects.last()
        assert registration.user == user
        assert days[0] not in registration.days.all()
        assert days[1] in registration.days.all()
        assert days[2] in registration.days.all()

    def test_update_registration(self, user, client, days):
        record = Registration.objects.create(user=user, country="BR")
        record.days.add(days[0])
        response = client.post(
            '/register/',
            {
                "days": [days[1].id],
                "country": "FR",
                "full_name": "Baz Qux",
            }
        )
        assert response.status_code == 302
        registration = Registration.objects.get(user=user)
        assert registration.days.get() == days[1]
        assert registration.country == "FR"

    def test_unauthenticated(self, db):
        client = Client()
        response = client.get("/register/")
        assert response.status_code == 302
        assert response["Location"].startswith("/accounts/login/")


class TestCancelRegistrationView:
    def test_cancel_registration(self, user, client):
        record = Registration.objects.create(user=user)
        response = client.post('/unregister/')
        assert response.status_code == 302
        assert Registration.objects.filter(user=user).count() == 0

    def test_cancel_registration_get(self, user, client):
        record = Registration.objects.create(user=user)
        response = client.get('/unregister/')
        assert response.status_code == 200
