from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("kontakty", views.kontakty, name="kontakty"),
    path("doprava", views.doprava, name="doprava"),
    path("reklamace", views.reklamace, name="reklamace"),
    path("rozmery", views.rozmery, name="rozmery"),
    path("ochrana-osobnich-udaju", views.ochrana, name="ochrana"),
    path("obchodni-podminky", views.obchodni_podminky, name="obchodni_podminky"),
    path("o-nas", views.about, name="about"),
    path("discover_your_set", views.discover_your_set, name="discover_your_set"),
    path("objednat_na_miru", views.objednat_na_miru, name="objednat_na_miru"),
    path("product_feed", views.product_feed, name="product_feed"),
    path("product_feed/fb", views.product_feed_fb, name="product_feed_fb"),
    path("katalog", views.catalog_product_list, name="katalog_vse"),
    path("akce/<str:token>/", views.akce, name="akce"),
    path("certifikaty", views.certificates, name="certificates"),
    path(
        "<slug:category_slug>",
        views.catalog_product_list,
        name="product_list_by_category",
    ),
    path("train_the_model/", views.train_the_model, name="train_the_model"),
    path(
        "recommendation_engine/",
        views.recommendation_engine_settings,
        name="recommendation_engine_settings",
    ),
    path(
        "media/assets/Reklamace.pdf",
        views.download_reklamacni_formular,
        name="download_reklamacni_formular",
    ),
    path("<int:id>/<slug:slug>", views.product_detail, name="product_detail"),
]
