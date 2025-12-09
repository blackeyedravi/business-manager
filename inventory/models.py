from django.db import models
import uuid

class Product(models.Model):

    ANIMAL_CHOICES = [
        ("Cow", "Cow"),
        ("Goat", "Goat"),
        ("Sheep", "Sheep"),
        ("Pig", "Pig"),
        ("Chicken", "Chicken"),
    ]

    MEAT_CHOICES = [
        ("Whole", "Whole"),
        ("Beef", "Beef"),
        ("Mutton", "Mutton"),
        ("Goat Meat", "Goat Meat"),
        ("Pork", "Pork"),
        ("Chicken", "Chicken"),
    ]

    animal_type = models.CharField(max_length=50, choices=ANIMAL_CHOICES)
    meat_type = models.CharField(max_length=50, choices=MEAT_CHOICES)

    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)

    cost_price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    selling_price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)

    stock = models.PositiveIntegerField(default=1)

    # ✅ Unique code for label / QR / reference
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------
    # Calculations
    # -------------------
    @property
    def total_cost(self):
        return self.weight_kg * self.cost_price_per_kg

    @property
    def total_selling_price(self):
        return self.weight_kg * self.selling_price_per_kg

    @property
    def name(self):
        return f"{self.animal_type} - {self.meat_type} ({self.weight_kg} kg)"

    def __str__(self):
        return self.name
