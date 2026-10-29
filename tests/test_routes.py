"""
Test cases for Product Routes.
"""
import os
import logging
import unittest
from decimal import Decimal
from service import app
from service.models import Product, Category, db
from service.common import status
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")
BASE_URL = "/products"


class TestProductRoutes(unittest.TestCase):
    """Test Cases for Product Routes."""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests."""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests."""
        db.session.close()

    def setUp(self):
        """Runs before each test."""
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test."""
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk."""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED,
                "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_read_a_product(self):
        """It should Read a single Product."""
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_update_a_product(self):
        """It should Update an existing Product."""
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        new_product["description"] = "Updated description for test"
        response = self.client.put(
            f"{BASE_URL}/{new_product['id']}", json=new_product
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "Updated description for test")

    def test_delete_a_product(self):
        """It should Delete a Product."""
        products = self._create_products(5)
        product_count = self.get_product_count()
        test_product = products[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_get_product_list(self):
        """It should Get a list of Products."""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_by_name(self):
        """It should Query Products by Name."""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([p for p in products if p.name == test_name])
        response = self.client.get(BASE_URL, query_string={"name": test_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_by_category(self):
        """It should Query Products by Category."""
        products = self._create_products(10)
        category = products[0].category
        category_products = [p for p in products if p.category == category]
        response = self.client.get(
            BASE_URL, query_string={"category": category.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_products))
        for product in data:
            self.assertEqual(product["category"], category.name)

    def test_query_by_availability(self):
        """It should Query Products by Availability."""
        products = self._create_products(10)
        available_products = [p for p in products if p.available is True]
        response = self.client.get(
            BASE_URL, query_string={"available": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(available_products))
        for product in data:
            self.assertEqual(product["available"], True)

    def get_product_count(self):
        """Helper to get the current product count."""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)
