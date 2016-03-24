# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.links.models import Link
from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.users.models import User


class LinkUsageByUserTest(WebTest):

    def test_top_teams_and_orgs(self):
        #   Create three orgs
        o1 = Organisation(name='org0001')
        o1.save()
        o2 = Organisation(name='org0002')
        o2.save()
        o3 = Organisation(name='org0003')
        o3.save()

        #   Create SEVEN teams!!! Grouped into organistions
        t1 = Team(name='team0001', organisation=o1)
        t1.save()
        t2 = Team(name='team0002', organisation=o1)
        t2.save()
        t3 = Team(name='team0003', organisation=o1)
        t3.save()
        t4 = Team(name='team0004', organisation=o2)
        t4.save()
        t5 = Team(name='team0005', organisation=o2)
        t5.save()
        t6 = Team(name='team0006', organisation=o3)
        t6.save()
        t7 = Team(name='team0007', organisation=o3)
        t7.save()

        #   Now we need three users, and throw them into teams
        u1 = User(slug='user0001', original_slug="user0001")
        u1.save()
        u1.teams.add(t2, t3, t4)
        u1.save()

        u2 = User(slug='user0002', original_slug="user0002")
        u2.save()
        u2.teams.add(t5, t6)
        u2.save()

        u3 = User(slug='user0003', original_slug="user0003")
        u3.save()
        u3.teams.add(t3, t5, t6, t7)
        u3.save()

        #   Last and not least we need a tool for everyone to use
        l1 = Link(
            name='link0001',
            is_external=True,
            owner=u1,
            destination='http://google.com'
        )
        l1.save()

        #   Now we need to log in each user and get them to click the external
        #   link button a few times each.
        #
        #   User 1, is going to use the tool 4 times.
        #   User 2, is going to use the tool 2 times.
        #   User 3, is going to use the tool 5 times.

        #   Login as the first user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        form.submit()

        interstitial_page_form = self.app.get(
            reverse('link-redirect', kwargs={'pk': l1.pk})).follow().form
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()

        #   Login as the second user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0002'
        form.submit()

        interstitial_page_form = self.app.get(
            reverse('link-redirect', kwargs={'pk': l1.pk})).follow().form
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()

        #   Login as the third user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0003'
        form.submit()

        interstitial_page_form = self.app.get(
            reverse('link-redirect', kwargs={'pk': l1.pk})).follow().form
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()
        interstitial_page_form.submit().follow()

        #   Now we've done all the clicks, lets go an have a look at the
        #   details page, and check out the teams and organisations usage
        #   count.
        details_page = self.app.get(
            reverse('link-detail', kwargs={'pk': l1.pk}))

        #   Due to the counting above, we know the teams have used the tool
        #   the following amount, so lets check for that...
        #   t1:0, t2:4, t3:9, t4:4, t5:7, t6:7, t7:5
        #   i.e. there are no members is team 1.
        #   only user 1 is in team 2.
        #   users 1 & 3 are in team 3.
        usage_by_teams = details_page.html.find(
            'ul',
            id='usage-by-teams'
        ).findAll('li')
        self.assertEquals(usage_by_teams[0].text,
                          'team0003 have collectively used the tool 9 times')
        self.assertEquals(usage_by_teams[1].text,
                          'team0005 have collectively used the tool 7 times')
        self.assertEquals(usage_by_teams[2].text,
                          'team0006 have collectively used the tool 7 times')
        self.assertEquals(usage_by_teams[3].text,
                          'team0007 have collectively used the tool 5 times')
        self.assertEquals(usage_by_teams[4].text,
                          'team0002 have collectively used the tool 4 times')

        #   We do a similar thing with organisations, which are tricky
        #   because user 1 is in team 2 & 3, so both those teams get the
        #   4 times user 1 used the tool. But teams 2 & 3 are both in org 1,
        #   and the code has made sure to only count the useage once, rather
        #   than 4 times from team 2 and 4 again from team 3. This checks
        #   that based on the numbers above the results are as follows.
        #   o1:9, o2:11, o3:7. Ordered that's o2,o1,o3.
        used_by_organisations = details_page.html.find(
            'ul',
            id='usage-by-organisations'
        ).findAll('li')
        self.assertEquals(used_by_organisations[0].text,
                          'org0002 have collectively used the tool 11 times')
        self.assertEquals(used_by_organisations[1].text,
                          'org0001 have collectively used the tool 9 times')
        self.assertEquals(used_by_organisations[2].text,
                          'org0003 have collectively used the tool 7 times')
