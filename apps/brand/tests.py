from django.test import TestCase
from .models import Brand

# Create your tests here.
class BrandModelTest(TestCase):
    def setUp(self):
        # self.store = Store.objects.create(name="Demo Store")
        self.brand = Brand.objects.create(name="Nike", store=self.store)
    
    def test_brand_creation(self):
        self.assertEqual(self.brand.name, "Nike")
        self.assertEqual(str(self.brand), "Nike - Demo Store")
