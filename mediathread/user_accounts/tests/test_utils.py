from django.test import TestCase
from django.conf import settings

from mediathread.user_accounts.utils import add_email_to_mailchimp_list

import mailchimp
from mock import patch, MagicMock

mock_mailchimp = MagicMock(spec=mailchimp)

"""
Exceptions
"""


class ApiKeyNotValid(Exception):
    pass


class ListIdNotValid(Exception):
    pass

"""
Test Cases
"""


#@patch("mailchimp.Mailchimp", mock_mailchimp)
class MailChimpTest(TestCase):
    def setUp(self):
        self.test_mailchimp_data = {
            'list_id': settings.MAILCHIMP_REGISTRATION_LIST_ID,
            'api_key': settings.MAILCHIMP_API_KEY
            }

        print 'Using list id: %s' % self.test_mailchimp_data['list_id']
        print 'Using api key: %s' % self.test_mailchimp_data['api_key']
        self.test_mailchimp_fields = {
            u'EMAIL': u'mediathreadtest@mediathread.com',
            u'FNAME': u'Tester',
            u'LNAME': u'Su',
            u'HEAR': u'Conference',
            u'ORG': u'Appsembler',
            u'TITLE': u'student'
            }

        self.ms = mailchimp.Mailchimp(self.test_mailchimp_data['api_key'])

    def test_api_key_valid(self):
        try:
            self.ms.lists.list()
        except:
            raise ApiKeyNotValid("Mailchimp API key is not valid")

    def test_registration_list_id_valid(self):
        try:
            self.ms.lists.merge_vars(id=[self.test_mailchimp_data['list_id']])
        except Exception as e:
            print e
            raise ListIdNotValid("Given list id is not valid")

    def test_subscribe_user(self):
        # subscribe user
        test_data = self.test_mailchimp_data
        test_fields = self.test_mailchimp_fields

        test_fields_arg = dict([(k.lower(), v) for k, v in test_fields.items()])
        result = add_email_to_mailchimp_list(test_fields['EMAIL'], test_data['list_id'], **test_fields_arg)
        test_email_struct = {
            'email': test_fields['EMAIL']
        }
        self.assertEqual(result, True)

        # check whether user exists in list
        result_memberinfo = self.ms.lists.member_info(id=test_data['list_id'], emails=[test_email_struct])
        from pprint import pprint
        pprint(result_memberinfo)
        self.assertEqual(result_memberinfo['error_count'], 0)

        # check user information is correct
        result_member = result_memberinfo['data'][0]
        result_member_merges = result_member['merges']

        """
        for k, v in test_fields.items():
            self.assertEqual(test_fields[k], result_member_merges[k])
        """
        self.assertDictEqual(test_fields, result_member_merges)


        # roll back
        self.ms.lists.unsubscribe(
            id=test_data['list_id'],
            email=test_email_struct,
            delete_member=True,
            send_goodbye=False,
            send_notify=False)
