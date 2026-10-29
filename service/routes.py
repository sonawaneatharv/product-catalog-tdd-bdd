"""
Product Store Service Routes.
"""
from flask import jsonify, request, url_for, abort
from service.models import Product, Category
from service.common import status
from service import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response."""
    return (
        jsonify(
            name="Product Catalog REST API Service",
            version="1.0",
            paths=url_for("list_products", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """Creates a Product."""
    app.logger.info("Request to create a product")
    check_content_type("application/json")
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with ID [%s] created.", product.id)
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """Retrieves a single Product."""
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """Update a Product."""
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)
    product.id = product_id
    product.update()
    app.logger.info("Product with ID [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Delete a Product."""
    app.logger.info("Request to Delete a product with id [%s]", product_id)
    product = Product.find(product_id)
    if product:
        app.logger.info("Product with ID [%s] found.", product.id)
        product.delete()
    app.logger.info("Product with ID [%s] delete complete.", product_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST / SEARCH PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Products, with optional filtering."""
    app.logger.info("Request to list Products...")
    products = []

    # Filter by name
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        app.logger.info("Filtering by name: %s", name)
        products = Product.find_by_name(name)
    elif category:
        app.logger.info("Filtering by category: %s", category)
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value)
    elif available:
        app.logger.info("Filtering by availability: %s", available)
        available_value = available.lower() in ["true", "1", "yes"]
        products = Product.find_by_availability(available_value)
    else:
        app.logger.info("Returning unfiltered list.")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# UTILITY FUNCTIONS
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct."""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
