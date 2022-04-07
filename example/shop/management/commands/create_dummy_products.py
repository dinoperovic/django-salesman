import json
import os
import random

from django.core.management.base import BaseCommand

from shop.models import Phone, PhoneVariant, Product


class Command(BaseCommand):
    help = "Create dummy products"

    def get_dummy_data(self, name):
        filepath = os.path.join(os.path.dirname(__file__), name)
        with open(filepath, "r") as f:
            return json.load(f)

    def handle(self, *args, **options):
        counts = {
            "products": 0,
            "phones": 0,
            "phone_variants": 0,
        }
        products = self.get_dummy_data("products.json")
        for data in products:
            _, created = Product.objects.update_or_create(id=data["id"], defaults=data)
            if created:
                counts["products"] += 1

        phones = self.get_dummy_data("phones.json")
        phone_combos = [
            (x[0], y[0]) for x in PhoneVariant.COLORS for y in PhoneVariant.CAPACITIES
        ]
        for data in phones:
            phone, created = Phone.objects.update_or_create(
                id=data["id"], defaults=data
            )
            if created:
                counts["phones"] += 1
            for color, capacity in phone_combos:
                variant, created = PhoneVariant.objects.update_or_create(
                    phone=phone, color=color, capacity=capacity
                )
                variant.price = random.randint(10, 500)
                variant.save(update_fields=["price"])
                if created:
                    counts["phone_variants"] += 1

        for key, count in counts.items():
            label = key.replace("_", " ").title()
            self.stdout.write(self.style.SUCCESS(f"Created {count} {label}"))
