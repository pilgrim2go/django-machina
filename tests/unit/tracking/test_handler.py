# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth import get_user
from django.db.models import get_model
from django.test.client import Client
from guardian.shortcuts import assign_perm

# Local application / specific library imports
from machina.core.loading import get_class
from machina.test.factories import create_category_forum
from machina.test.factories import create_forum
from machina.test.factories import create_link_forum
from machina.test.factories import create_topic
from machina.test.factories import GroupFactory
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.testcases import BaseUnitTestCase

Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('tracking', 'ForumReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
TrackingHandler = get_class('tracking.handler', 'TrackingHandler')


class TestTrackingHandler(BaseUnitTestCase):
    def setUp(self):
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.g1 = GroupFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.top_level_cat_1 = create_category_forum()
        self.top_level_cat_2 = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat_1)
        self.forum_2 = create_forum(parent=self.top_level_cat_1)
        self.forum_2_child_1 = create_link_forum(parent=self.forum_2)
        self.forum_2_child_2 = create_forum(parent=self.forum_2)
        self.forum_3 = create_forum(parent=self.top_level_cat_1)

        self.forum_4 = create_forum(parent=self.top_level_cat_2)

        self.topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=self.topic, poster=self.u1)

        # Initially u2 read the previously created topic
        ForumReadTrackFactory.create(forum=self.forum_2, user=self.u2)

        # Assign some permissions
        assign_perm('can_read_forum', self.g1, self.top_level_cat_1)
        assign_perm('can_read_forum', self.g1, self.top_level_cat_2)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2_child_2)

    def test_says_that_all_forums_are_read_for_users_that_are_not_authenticated(self):
        # Setup
        u3 = get_user(Client())
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), u3)
        # Check
        self.assertFalse(len(unread_forums))

    def test_cannot_say_that_a_forum_is_unread_if_it_is_not_visible_by_the_user(self):
        # Setup
        new_topic = create_topic(forum=self.forum_3, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        unread_forums = self.tracks_handler.get_unread_forums(Forum.objects.all(), self.u2)
        # Check
        self.assertNotIn(self.forum_3, unread_forums)

    def test_says_that_all_topics_are_read_for_users_that_are_not_authenticated(self):
        # Setup
        u3 = get_user(Client())
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), u3)
        # Check
        self.assertFalse(len(unread_topics))

    def test_says_that_a_topic_with_a_creation_date_greater_than_the_forum_mark_time_is_unread(self):
        # Setup
        new_topic = create_topic(forum=self.forum_2, poster=self.u1)
        PostFactory.create(topic=new_topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        self.assertEqual(unread_topics, [new_topic, ])

    def test_says_that_a_topic_with_an_update_date_greater_than_the_forum_mark_time_is_unread(self):
        # Setup
        PostFactory.create(topic=self.topic, poster=self.u1)
        # Run
        unread_topics = self.tracks_handler.get_unread_topics(self.forum_2.topics.all(), self.u2)
        # Check
        self.assertEqual(unread_topics, [self.topic, ])