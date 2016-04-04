# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import create_team
from testing.common import generate_fake_links


class TeamToolUsageTests(WebTest):
    def test_list_top_tools_ordered(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        t = create_team(
            name='Two members top teams', num_members=2
        )

        user1 = t.user_set.all()[0]

        (self.el1, self.el2,
         self.el3, self.el4,
         self.el5, self.el6,
         self.el7, self.el8,
         self.el9, self.el10) = generate_fake_links(
            user1,
            count=10,
            is_external=True
        )

        for i in range(0, 8):
            self.el4.register_usage(user1)

        for i in range(0, 6):
            self.el8.register_usage(user1)

        for i in range(0, 5):
            self.el3.register_usage(user1)

        for i in range(0, 4):
            self.el1.register_usage(user1)

        for i in range(0, 2):
            self.el9.register_usage(user1)

        for i in range(0, 1):
            self.el10.register_usage(user1)

        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        tools_list = response.html.find(id="top_links_list")
        tools_list_items = tools_list.findChildren('a')

        self.assertEqual(
            len(tools_list_items),
            5
        )
        self.assertIn(
            self.el4.name,
            tools_list_items[0].text
        )
        self.assertIn(
            self.el8.name,
            tools_list_items[1].text
        )
        self.assertIn(
            self.el3.name,
            tools_list_items[2].text
        )
        self.assertIn(
            self.el1.name,
            tools_list_items[3].text
        )
        self.assertIn(
            self.el9.name,
            tools_list_items[4].text
        )
        self.assertNotIn(
            self.el10.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el2.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el5.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el6.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el7.name,
            tools_list.text
        )
