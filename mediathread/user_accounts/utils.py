from django.conf import settings

import mailchimp


def add_email_to_mailchimp_list(email_address, list_id, **kwargs):
    merge_vars_dict = {}

    for k, v in kwargs.items():
        merge_vars_dict[k.upper()] = v

    if not settings.MAILCHIMP_API_KEY:
        print "did not defined api key for Mailchimp, skip Mailchimp related action now"
        return False

    ms = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)

    # new version API require email as a struct with an email field.
    email_struct = {
        'email': email_address
        }

    ms.lists.subscribe(
        id=list_id,
        email=email_struct,
        merge_vars=merge_vars_dict,
        update_existing=True,
        double_optin=False)

    return True


def display_user(user):
    if user.first_name or user.last_name:
        return user.get_full_name()
    else:
        return user.username
