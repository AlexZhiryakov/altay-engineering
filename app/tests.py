from django.test import TestCase
from django.utils import timezone

from app.models import Product, Request
from app.views import generate_order_pdf


class CatalogTests(TestCase):
    fixtures = ["catalog"]

    def test_public_pages_open(self):
        urls = [
            "/",
            "/shopping-cart",
            "/privacy-policy",
            "/terms-of-use",
            "/cookie-policy",
            "/refund-policy",
            "/company/aboutCompany",
            "/company/details",
            "/catalog/welding-machines",
            "/catalog/fitting",
            "/catalog/pipes",
            "/catalog/shut-off-valves",
            "/service/welding-equipment/rental",
            "/service/welding-equipment/repair",
            "/service/pipeline-installation",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_home_page_opens(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AlexZhiryakov")

    def test_category_page_shows_products(self):
        response = self.client.get("/catalog/welding-machines/hydraulic")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Гидравлические")
        self.assertContains(response, "product-item")

    def test_filter_uses_model_field(self):
        product = (
            Product.objects.filter(category__name="Гидравлические сварочные аппараты")
            .exclude(welding_range="")
            .first()
        )
        self.assertIsNotNone(product)
        response = self.client.get(
            "/catalog/welding-machines/hydraulic",
            {"welding_range": product.welding_range},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, product.name)

    def test_add_to_cart_toggles(self):
        product = Product.objects.first()
        added = self.client.post("/add-to-cart", {"product_id": product.id})
        self.assertEqual(added.status_code, 200)
        self.assertTrue(added.json()["in_cart"])
        self.assertEqual(self.client.session["cart"][str(product.id)], 1)

        removed = self.client.post("/add-to-cart", {"product_id": product.id})
        self.assertFalse(removed.json()["in_cart"])
        self.assertNotIn(str(product.id), self.client.session.get("cart", {}))

    def test_order_success_is_public(self):
        order = Request.objects.create(
            customer_name="Тест",
            customer_phone="+70000000000",
            customer_email="demo@example.com",
            privacy_policy_accepted=True,
        )
        session = self.client.session
        session["last_request_id"] = order.id
        session.save()
        response = self.client.get("/request-success/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{order.id}")

    def test_place_order_is_available_without_login(self):
        product = Product.objects.first()
        self.client.post("/add-to-cart", {"product_id": product.id})
        response = self.client.post(
            "/place-order/",
            {
                "name": "Иван",
                "phone": "+79990000000",
                "email": "ivan@example.com",
                "comment": "тест",
                "privacy_policy": "on",
            },
        )
        self.assertRedirects(response, "/request-success/")
        self.assertEqual(Request.objects.count(), 1)

    def test_order_pdf_contains_cyrillic_document(self):
        order = Request.objects.create(
            customer_name="Иван",
            customer_phone="+79990000000",
            customer_email="ivan@example.com",
            privacy_policy_accepted=True,
            privacy_policy_accepted_at=timezone.now(),
            total_price=100,
        )
        pdf = generate_order_pdf(
            order,
            [{"name": "Труба ПНД", "quantity": 2, "price": 50, "total": 100}],
        )
        self.assertIsNotNone(pdf)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_product_page_shows_characteristic(self):
        product = Product.objects.exclude(manufacturer="").first()
        response = self.client.get(f"/product/{product.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Производитель")
        self.assertContains(response, product.manufacturer)
