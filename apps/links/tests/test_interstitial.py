# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
from apps.users.models import User

from django_webtest import WebTest


class LinksWithInterstitialTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            slug='user0001',
            username='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        user_id = response.html.find_all(
                'span', attrs={'class': 'user_id'}
            )[0].text
        self.assertEquals(user_id, 'user0001')

        self.external_link = Link(
            name='Tweetbot',
            description='A great twitter application',
            destination='https://tweetbot.com',
            owner=self.logged_in_user,
            is_external=True,)
        self.external_link.save()

        self.internal_link = Link(
            name='Not Wikimapia',
            description='Pretend this is not Wikimapia',
            destination='https://wikimapia.org',
            owner=self.logged_in_user,
            is_external=False,)
        self.internal_link.save()

    def test_external_link_goes_to_interstitial(self):
        response = self.app.get(
            reverse('link-detail', kwargs={'pk': self.external_link.pk}))

        response = response.click(linkid="link_follow_button")

        confirm_button = response.html.find(id="confirm_redirect_button")
        cancel_button = response.html.find(id="cancel_button")

        self.assertEquals(
            confirm_button.attrs['href'],
            self.external_link.destination
        )

        self.assertEquals(
            cancel_button.attrs['href'],
            reverse('link-detail', kwargs={'pk': self.external_link.pk})
        )

        self.assertIsNotNone(confirm_button)

    def test_internal_link__does_not_go_to_interstitial(self):
        response = self.app.get(
            reverse('link-detail', kwargs={'pk': self.internal_link.pk}))

        response = response.click(linkid="link_follow_button").follow()

        confirm_button = response.html.find(id="confirm_redirect_button")
        cancel_button = response.html.find(id="cancel_button")

        self.assertIsNone(cancel_button)
        self.assertIsNone(confirm_button)
