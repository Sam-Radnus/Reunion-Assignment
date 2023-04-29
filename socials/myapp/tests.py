from django.test import TestCase
from .models import User,Post
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
# Create your tests here.
class UserTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword'
        )
        
    def test_user_creation(self):
        self.assertIsInstance(self.user, User)
        
    def test_user_email_uniqueness(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                username='testuser2',
                password='testpassword'
            )
            
    def test_user_total_followers(self):
        self.assertEqual(self.user.total_followers(), 0)
        
    def test_user_total_following(self):
        self.assertEqual(self.user.total_following(), 0)
        
    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser')
        
    def test_user_username_field(self):
        self.assertEqual(self.user.username, 'testuser')
        
    def test_user_required_fields(self):
        self.assertEqual(User.REQUIRED_FIELDS, ['username'])

class PostModelTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass'
        )
        self.post = Post.objects.create(
            name='Test post',
            caption='Test caption',
            user=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_post_creation_successful(self):
        """
        Test if a post is created successfully when all required parameters are provided with the correct format.
        """
        url = reverse('all_posts')
        data = {
            'name': 'New post',
            'caption': 'New caption'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.last().name, 'New post')
        self.assertEqual(Post.objects.last().caption, 'New caption')
        self.assertEqual(Post.objects.last().user, self.user)
        
    def test_post_creation_title_missing(self):
        """
        Test if a post creation is unsuccessful when the Title field is missing in the POST request.
        """
        url = reverse('all_posts')
        data = {
            'caption': 'New caption'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.last().name, 'Test post')
        self.assertEqual(Post.objects.last().caption, 'Test caption')
        self.assertEqual(Post.objects.last().user, self.user)