import csv
from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mail_confirmation import certificate_order_email_confirmation
from .models import Order, OrderItem
from .services import OrderStatusService


@admin.action(description="📧 Poslat certifikát emailem")
def send_certificate_email(modeladmin, request, queryset):
    for order in queryset:
        certificate_order_email_confirmation(order.id)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = (
        "product",
        "zpusob_vyroby",
        "order",
        "velikost",
        "poznamka",
        "price",
        "quantity",
        "slevovy_kod",
        "hodnota_kuponu",
        "certificate_from",
        "certificate_to",
    )

    raw_id_fields = [
        "product",
    ]  # or use autocomplete_fields = ("product",) for autocomplete

    class Meta:
        ordering = (
            "product__name",
            "velikost",
            "price",
            "quantity",
            "order",
        )

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Cancel Button Functionality
    # HTML templates
    change_form_template = "orders/change_form.html"

    # Figure out url path
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:order_id>/cancel/",
                self.admin_site.admin_view(self.cancel_order_view),
                name="orders-order-cancel",
            ),
        ]

        return custom_urls + urls

    # create a view
    def cancel_order_view(self, request, order_id):
        from django.shortcuts import get_object_or_404, redirect

        from orders.models import Order

        order = get_object_or_404(Order, pk=order_id)

        OrderStatusService.mark_as_cancelled(order)

        return redirect(f"../../{order_id}/change/")

    # Define the button visuals
    def cancel_button(self, obj):
        if not obj or obj.status == "S":
            return ""

        url = reverse("admin:orders-order-cancel", args=[obj.pk])

        return format_html(
            '<a class="button" style="background:#ba2121;color:white" href="{}">'
            "Storno objednávky</a>",
            url,
        )

    cancel_button.short_description = "Storno"

    list_display = [
        "etb_id",
        "products",
        "short_description",
        "total_cost",
        "status",
        "created",
        "paid",
        "author_comment",
        "first_name",
        "last_name",
        "email",
        "number",
        "newsletter_consent",
        "comments",
        "shipping",
        "address",
        "created",
        "discount_code",
        "download_label",
        "updated",
    ]

    fieldsets = (
        (
            "Order Identification",
            {
                "fields": (
                    "etb_id",
                    "author_comment",
                    "confirmation_sent",
                    "paid_confirmation_sent",
                    "shipped_sent",
                    "created",
                    "updated",
                ),
                "description": "Internal tracking and timestamps.",
            },
        ),
        (
            "Order Status & Communication",
            {
                "classes": ("wide",),
                "fields": (
                    ("status",),
                    ("order_created", "paid", "shipped"),
                    ("cancel_button", "cancelled"),
                ),
            },
        ),
        (
            "Customer Information",
            {
                "fields": (
                    ("first_name", "last_name"),
                    ("email", "number"),
                    "birthday",
                    "newsletter_consent",
                    "comments",
                )
            },
        ),
        (
            "Shipping Details",
            {
                "fields": (
                    "shipping",
                    "vendor_id",
                    "address",
                    ("city", "zipcode", "country"),
                    ("zasilkovna_id", "label"),
                )
            },
        ),
        (
            "Payment & Totals",
            {
                "fields": (
                    ("total_cost", "shipping_price"),
                    ("discount", "discount_code", "coupon_id"),
                    "stripe_id",
                )
            },
        ),
    )

    readonly_fields = [
        "confirmation_sent",
        "paid_confirmation_sent",
        "shipped_sent",
        "created",
        "updated",
        "status",
        "cancel_button",
        "cancelled",
    ]

    inlines = [OrderItemInline]

    def send_manual_confirmation(self, obj):
        pass

    send_manual_confirmation.short_description = "Send Manual Confirmation"

    def download_label(self, obj):
        if obj.label:
            file_name = obj.label.split("/")[-1].replace(".pdf", "")
            url = reverse("orders:download_ppl_label", args=[file_name])
            return mark_safe(f'<a href="{url}" download>PPL Etiketa</a>')
        else:
            url = reverse("stripepayment:manually_create_PPL", args=[obj.id])
            return mark_safe(f'<a href="{url}">Vytvořit etiketu</a>')

    download_label.short_description = "PDF Label"

    # list_editable = ["shipped"]  # Add the "shipped" field to make it editable

    def get_total_cost(self, obj):
        return obj.get_total_cost()  # Call the Order's get_total_cost() method

    get_total_cost.short_description = (
        "Total Cost"  # Set the column header in the admin site
    )

    def price(self, obj):
        price_value = obj.items.values_list("price").first()
        return str(price_value[0])

    def quantity(self, obj):
        quantity_value = obj.items.values_list("quantity").first()
        if (
            quantity_value is not None and quantity_value
        ):  # Check for both None and an empty list
            return str(quantity_value[0])
        else:
            return "N/A"  # or some default value

    def velikosti(self, obj):
        items = obj.items.all()
        item_details = []
        for item in items:
            item_details.append(f"{item.velikost}")
            item_details.append(f"kalhotky_velikost_set: {item.kalhotky_velikost_set}")
            item_details.append(
                f"podprsenka_velikost_set: {item.podprsenka_velikost_set}"
            )
            item_details.append(f"pas_velikost_set: {item.pas_velikost_set}")

        return ", ".join(item_details)

    def druh_kolekce(self, obj):
        value = 0
        return str(value)

    def products(self, obj):
        product_names = [item.product.name for item in obj.items.all()]

        return product_names

    def short_description(self, obj):
        product_desc = [item.product.short_description for item in obj.items.all()]
        return product_desc

    velikosti.short_description = "Položky v objednávce"

    def has_add_permission(self, request, obj=None):
        return True

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Set instance price equal to product price
            instance.price = instance.product.price
            instance.save()
        formset.save_m2m()

    """ def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = 'attachment; filename="orders.xls"'

        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet("Orders")

        row_num = 0

        columns = [
            "etb_id",
            "products",
            "total_cost",
            "paid",
            "shipped",
            "first_name",
            "last_name",
            "email",
            "number",
            "newsletter_consent",
            "comments",
            "shipping",
            "address",
        ]

        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title)

        for obj in queryset:
            row_num += 1
            row = [
                obj.etb_id,
                ", ".join([item.product.name for item in obj.items.all()]),
                obj.paid,
                obj.shipped,
                obj.first_name,
                obj.last_name,
                obj.email,
                obj.number,
                obj.newsletter_consent,
                obj.comments,
                obj.shipping,
                obj.address,
            ]
            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, cell_value)

        wb.save(response)
        return response

    export_to_excel.short_description = "Exportovat do Excelu"

    actions = ["export_to_excel"]
"""

    def export_to_csv(self, request, queryset):
        def fix_order_date(dt_str):
            try:
                dt_str = str(dt_str)
                dt_obj = datetime.fromisoformat(dt_str)
            except ValueError:
                return None

            return dt_obj.replace(microsecond=0, tzinfo=None).isoformat()

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)

        writer.writerow(
            [
                "order_external_order_id",
                "order_date",
                "order_value",
                "order_currency",
                "order_external_order_state",
                "identification_email_address",
                "identification_first_name",
                "identification_last_name",
                "identification_phone",
                "identification_external_user_id",
                "identification_address_house_number",
                "identification_address_street",
                "identification_address_city",
                "identification_address_zip_code",
                "identification_address_country_code",
                "product_external_product_id",
                "product_name",
                "product_value",
                "product_currency",
                "product_quantity",
            ]
        )

        for obj in queryset:
            date_created = fix_order_date(obj.created)
            products = ", ".join([item.product.name for item in obj.items.all()])
            writer.writerow(
                [
                    obj.etb_id,
                    date_created,
                    float(obj.total_cost),
                    "CZK",
                    obj.shipped,
                    obj.email,
                    obj.first_name,
                    obj.last_name,
                    obj.number,
                    obj.etb_id,
                    "N/A",
                    obj.address,
                    obj.city,
                    obj.zipcode,
                    obj.country,
                    obj.etb_id,
                    products,
                    0,
                    "CZK",
                    1,
                ]
            )

        return response

    export_to_csv.short_description = "Exportovat do CSV"

    actions = ["export_to_csv", send_certificate_email]
