from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from .models import Category
from .views import CategoryCreateListView

User = get_user_model()


class CategoryTest(APITestCase):
    def setUp(self, *args, **kwargs):
        self.factory = APIRequestFactory()
        self.setup_category()
        self.user = self.setup_user()

    def setup_user(self):
        return User.objects.create_superuser('test@gmail.com', '1')

    def setup_category(self):
        list_categories = []
        for i in range(1, 101):
            list_categories.append(Category(name=f'category{i}'))
        Category.objects.bulk_create(list_categories)

    def test_get_category(self):
        request = self.factory.get('/categories/')
        view = CategoryCreateListView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert Category.objects.count() == 100
        assert Category.objects.first().name == 'category1'

    def test_post_category(self):
        data = {
            'name': 'test_category'
        }
        request = self.factory.post('/categories/', data)
        force_authenticate(request, user=self.user)
        view = CategoryCreateListView.as_view()
        response = view(request)

        assert response.status_code == 201
        assert Category.objects.filter(name='test_category').exists()
