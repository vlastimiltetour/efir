from decimal import Decimal
from types import SimpleNamespace

import pytest

from cart.cart import Cart
from catalog.models import Category, Product


class CartSession(dict):
    modified = False


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Podprsenky", slug="podprsenky")
    return Product.objects.create(
        category=category,
        name="Test product",
        slug="test-product",
        price=100,
    )


@pytest.fixture
def cart():
    request = SimpleNamespace(session=CartSession())
    return Cart(request)


def test_add_saves_product_details_in_the_session(cart, product):
    cart.add(
        product,
        quantity=2,
        velikost="M",
        zpusob_vyroby="Skladem",
        color="Modrá",
    )

    assert len(cart) == 2
    assert len(cart.cart) == 1
    item = next(iter(cart.cart.values()))
    assert item["product_id"] == product.pk
    assert item["quantity"] == 2
    assert item["price"] == "100"
    assert item["velikost"] == "M"
    assert item["zpusob_vyroby"] == "Skladem"
    assert item["color"] == "Modrá"
    assert cart.session.modified is True


def test_add_keeps_different_product_variants_as_separate_items(cart, product):
    cart.add(product, quantity=1, velikost="M", color="Modrá")
    cart.add(product, quantity=1, velikost="L", color="Černá")

    assert len(cart) == 2
    assert len(cart.cart) == 2
    assert {(item["color"], item["velikost"]) for item in cart.cart.values()} == {
        ("Modrá", "M"),
        ("Černá", "L"),
    }


def test_add_calculates_custom_made_surcharge(cart, product):
    cart.add(product, quantity=2, zpusob_vyroby="Na Míru")

    item = next(iter(cart.cart.values()))
    assert Decimal(item["surcharge"]) == Decimal("30")
    assert cart.get_total_surcharge() == Decimal("60")


def test_update_quantity_changes_cart_item_and_total_count(cart, product):
    cart.add(product, quantity=1)
    item_id = next(iter(cart.cart))

    cart.update_quantity(item_id, 4)

    assert cart.cart[item_id]["quantity"] == 4
    assert len(cart) == 4
    assert cart.session.modified is True


def test_iter_returns_product_and_calculated_line_total(cart, product):
    cart.add(product, quantity=3)

    item = next(iter(cart))

    assert item["product"] == product
    assert item["price"] == Decimal("100")
    assert item["total_price"] == Decimal("300")


def test_clear_removes_cart_from_session(cart, product):
    cart.add(product)

    cart.clear()

    assert "cart" not in cart.session
    assert len(cart) == 0
    assert cart.session.modified is True
