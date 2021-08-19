from huscy.email_recruitment.models import InvitationEMail, ReminderEMail


def create_invitation_email(project, text, footer=''):
    return InvitationEMail.objects.create(project=project, text=text, footer=footer)


def create_reminder_email(project, text, footer=''):
    return ReminderEMail.objects.create(project=project, text=text, footer=footer)


def delete_invitation_email(invitation_email):
    invitation_email.delete()


def delete_reminder_email(reminder_email):
    reminder_email.delete()


def get_invitation_emails(project=None):
    queryset = InvitationEMail.objects.all()
    if project is None:
        return queryset
    return queryset.filter(project=project)


def get_reminder_emails(project=None):
    queryset = ReminderEMail.objects.all()
    if project is None:
        return queryset
    return queryset.filter(project=project)


def update_invitation_email(invitation_email, text, footer=''):
    invitation_email.text = text
    invitation_email.footer = footer or invitation_email.footer
    invitation_email.save()
    return invitation_email


def update_reminder_email(reminder_email, text, footer=''):
    reminder_email.text = text
    reminder_email.footer = footer or reminder_email.footer
    reminder_email.save()
    return reminder_email
