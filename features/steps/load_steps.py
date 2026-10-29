"""
Load Steps for BDD - loads test data (products) into the database.
"""
from behave import given
from service.models import Product
from tests.factories import ProductFactory


@given("the following products")
def step_impl(context):
    """Delete all Products and load new ones from the data table."""
    # Clear the database
    Product.remove_all()
    # Load the test data from the feature file table
    for row in context.table:
        product = ProductFactory()
        product.name = row["name"]
        product.description = row["description"]
        product.price = float(row["price"])
        product.available = row["available"].lower() in ["true", "1", "yes"]
        product.category = getattr(
            Product.Category, row["category"].upper(), Product.Category.UNKNOWN
        )
        product.create()
