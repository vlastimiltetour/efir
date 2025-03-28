from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="Váš slevový kód:")
    valid_from = models.DateField()
    valid_to = models.DateField()
    capacity = models.IntegerField(default=1, verbose_name="Počet")
    active = models.BooleanField(verbose_name="Aktivní")
    redeemed = models.BooleanField(default=False, verbose_name="Uplatněno")

    DISCOUNT_TYPES = [
        ("Procento", "Procento"),
        ("Částka", "Částka"),
    ]
    discount_type = models.CharField(
        max_length=255,
        choices=DISCOUNT_TYPES,
        verbose_name="Typ slevy",
        blank=True,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Zadejte hodnotu 0. anebo absolutní hodnotu částky",
        blank=False,
        default=0,
    )
    discount_threshold = models.DecimalField(
        verbose_name="Minimální částka pro uplatnění slevy",
        max_digits=10,
        decimal_places=0,
        blank=False,
        default=0,
        null=True,
    )

    order_id = models.CharField(
        max_length=10, default="N/A", verbose_name="Nakoupeno v objednavce (ID)"
    )
    certificate_from = models.CharField(
        max_length=110, default="-", verbose_name="Do koho"
    )
    certificate_to = models.CharField(max_length=110, default="-", verbose_name="Komu")

    category_types = [
        ("Dárkový certifikát", "Dárkový certifikát"),
        ("Sleva na první nákup", "Sleva na první nákup"),
        ("Odměna 30 dní po 1. nákupu", "Odměna 30 dní po 1. nákupu"),
        (
            "Sleva po 3 měsících", "Sleva po 3 měsících"
        ),
        ("Přání k svátku", "Přání k svátku"),
        ("Osobní slevový kód", "Osobní slevový kód"),
("-", "-"),
    ]

    category = models.CharField(
        max_length=100,
        choices=category_types,
        verbose_name="Kategorie",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Sleva"
        verbose_name_plural = "Slevy"
