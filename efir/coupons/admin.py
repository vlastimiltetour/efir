import csv
from datetime import datetime

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from .models import Coupon
from .views import generate_voucher_code


class GenerateCouponsForm(forms.ModelForm):
    class Meta:
        model = Coupon
        exclude = ["code"]

    def save(self, commit=True):
        instance = super().save(commit=False)  # This calls ModelForm.save()
        instance.code = generate_voucher_code(8)  # Auto-generate code
        if commit:
            instance.save()
        return instance


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "category",
        "order_id",
        "valid_from",
        "valid_to",
        "discount_type",
        "active",
        "redeemed",
        "discount_threshold",
        "capacity",
        "discount_value",
        "certificate_from",
        "certificate_to",
    ]
    list_filter = ["active", "valid_from", "valid_to", "category"]
    search_fields = ["code"]

    change_list_template = "admin/coupons_changelist.html"  # Extend this template

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_new_coupons/",
                self.admin_site.admin_view(self.generate_new_coupons),
                name="generate_new_coupons",
            ),
        ]

        return custom_urls + urls

    def generate_new_coupons(self, request):
        if request.method == "POST":
            form = GenerateCouponsForm(request.POST)
            if form.is_valid():
                # Save instance, which sets code automatically
                count = form.cleaned_data["capacity"]
                coupons_created = 0
                base_data = {
                k: v for k, v in form.cleaned_data.items()
                if k not in ["capacity", "code"]
            }
                for _ in range(count): 
                    
                    Coupon.objects.create(code=generate_voucher_code(8), **base_data)
                    coupons_created += 1

                self.message_user(request, "Kupón úspěšně vygenerován.")
                return redirect("..")

        else:
            form = GenerateCouponsForm()
        context = {"form": form}

        return render(request, "admin/generate_coupons.html", context)

    @staticmethod
    def transfer_date(input_date):
        try:
            date = datetime.strptime(str(input_date), "%Y-%m-%d")
            transformed_date = date.strftime("%d.%m.%Y")  # Correct usage of strftime
            return transformed_date
        except ValueError:
            return "Invalid Format Date"

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="coupons.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "code",
                "valid_to",  # Adjust header names as needed
            ]
        )

        for obj in queryset:
            writer.writerow(
                [
                    obj.code,
                    self.transfer_date(obj.valid_to),  # Call transfer_date method
                ]
            )

        return response

    export_to_csv.short_description = "Exportovat kódy do Leadhub do CSV"

    actions = ["export_to_csv"]
