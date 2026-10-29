"""
Test cases for Product Model.
"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")


class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model."""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite."""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite."""
        db.session.close()

    def setUp(self):
        """This runs before each test."""
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test."""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_read_a_product(self):
        """It should Read a Product."""
        product = ProductFactory()
        logger.info("Testing reading a product: %s", product.name)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product."""
        product = ProductFactory()
        logger.info("Testing updating a product: %s", product.name)
        product.id = None
        product.create()
        logger.info("Created product: %s", product)
        self.assertIsNotNone(product.id)
        # Update it
        product.description = "Updated description"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "Updated description")
        # Fetch it back and verify
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "Updated description")

    def test_delete_a_product(self):
        """It should Delete a Product."""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # Delete it
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database."""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find Products by Name."""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([p for p in products if p.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_category(self):
        """It should Find Products by Category."""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([p for p in products if p.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_availability(self):
        """It should Find Products by Availability."""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([p for p in products if p.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)
