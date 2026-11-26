from unittest.mock import patch

import pytest
from django.conf import settings
from django.urls import reverse

from cart.cart import Cart
from cart.forms import CartAddProductForm
from catalog.models import Category, Color, Product, ProductVariant, ZpusobVyroby
from orders.models import OrderItem


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Podprsenky", slug="podprsenky")
    stock = ZpusobVyroby.objects.create(size="Skladem")
    product = Product.objects.create(
        category=category,
        name="Test product",
        slug="test-product",
        price=100,
    )
    product.zpusob_vyroby.add(stock)
    color = Color.objects.create(name="Modrá")
    ProductVariant.objects.create(product=product, color=color)
    return product


def add_to_cart_data(color="Modrá"):
    return {
        "quantity": "1",
        "color": color,
        "velikost": "",
        "zpusob_vyroby": "Skladem",
        "override": "",
        "poznamka": "Nepovinná poznámka",
        "kalhotky_velikost_set": "",
        "podprsenka_velikost_set": "",
        "pas_velikost_set": "",
        "certificate_from": "Odesílatel",
        "certificate_to": "Příjemce",
    }


@pytest.mark.django_db
def test_add_form_only_accepts_a_color_assigned_to_the_product(product):
    valid_form = CartAddProductForm(
        product.pk, data=add_to_cart_data(color="Modrá")
    )
    invalid_form = CartAddProductForm(
        product.pk, data=add_to_cart_data(color="Červená")
    )

    assert valid_form.is_valid(), valid_form.errors
    assert valid_form.cleaned_data["color"] == "Modrá"
    assert not invalid_form.is_valid()
    assert "color" in invalid_form.errors


@pytest.mark.django_db
def test_product_detail_renders_its_color_selector(client, product):
    response = client.get(product.get_absolute_url())

    assert response.status_code == 200
    assert b'name="color"' in response.content
    assert "Modrá" in response.content.decode()


@pytest.mark.django_db
def test_add_product_view_saves_selected_color_in_session_cart(client, product):
    response = client.post(
        reverse("cart:cart_add", args=[product.pk]),
        data=add_to_cart_data(),
    )

    cart_items = client.session[settings.CART_SESSION_ID].values()
    assert response.status_code == 302
    assert len(cart_items) == 1
    assert next(iter(cart_items))["color"] == "Modrá"


@pytest.mark.django_db
def test_checkout_copies_cart_color_to_order_item(client, product):
    session = client.session
    session[settings.CART_SESSION_ID] = {
        "cart-item-1": {
            "item_id": "cart-item-1",
            "product_id": product.pk,
            "color": "Modrá",
            "quantity": 1,
            "price": "100",
            "surcharge": "0",
            "velikost": "M",
            "kalhotky_velikost_set": "",
            "podprsenka_velikost_set": "",
            "pas_velikost_set": "",
            "poznamka": "",
            "zpusob_vyroby": "Skladem",
            "override": False,
            "certificate_from": "",
            "certificate_to": "",
        }
    }
    session["cart_country"] = "CZ"
    session["cart_address"] = "Test address"
    session["cart_vendor"] = "-"
    session["cart_shipping"] = "D"
    session["cart_city"] = "Praha"
    session["cart_zipcode"] = "11000"
    session.save()

    with (
        patch.object(Cart, "get_shipping_price", return_value=0),
        patch.object(Cart, "get_total_price_after_discount", return_value=100),
        patch.object(Cart, "transfer_discount_to_orders", return_value=0),
    ):
        response = client.post(
            reverse("cart:cart_detail"),
            data={
                "first_name": "Test",
                "last_name": "Customer",
                "email": "test@example.com",
                "number": "123456789",
                "shipping": "D",
                "address": "Test address",
                "country": "CZ",
                "vendor_id": "-",
                "agree_to_terms": "on",
            },
        )

    order_item = OrderItem.objects.get(product=product)
    assert response.status_code == 302
    assert order_item.color == "Modrá"
