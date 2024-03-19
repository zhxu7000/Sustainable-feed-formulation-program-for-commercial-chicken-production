from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class Recipe(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected = models.BooleanField(null=True, blank=True, default=True)
    total_cost_pre = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    total_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    tonne = models.DecimalField(
        max_digits=99999, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Tonne"
    )

    def __str__(self):
        return self.name


class RecipeRawMaterial(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255)
    price_per_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Price per kg",
    )
    max_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100,
        verbose_name="Max Percentage (%)",
    )
    min_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name="Min Percentage (%)",
    )
    min_weight_kg_per_ton = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        default=0,
        verbose_name="Min Weight (kg/ton)",
    )
    max_weight_kg_per_ton = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        default=1000,
        verbose_name="Max Weight (kg/ton)",
    )

    class Meta:
        unique_together = ("recipe", "material_name")

    selected = models.BooleanField(null=True, blank=True, default=True)


class RecipeAttributeLimit(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    attribute_name = models.CharField(max_length=255)
    min_value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Min Value",
        default=0.0,
    )
    max_value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Max Value",
        default=999.9,
    )
    selected = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        unique_together = ("attribute_name", "recipe")

    def __str__(self):
        return f"{self.recipe.name} - {self.attribute_name} (Min: {self.min_value}, Max: {self.max_value})"


class MaterialAttributeValue(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        "Recipe", null=True, blank=True, on_delete=models.CASCADE
    )
    raw_material = models.ForeignKey(RecipeRawMaterial, on_delete=models.CASCADE)
    attribute_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=10)
    selected = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        unique_together = ("attribute_name", "raw_material")


class BestRecipe(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    material = models.ForeignKey(RecipeRawMaterial, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="percentage",
    )

    class Meta:
        unique_together = ("recipe", "material_name")


class BestRecipeNutrition(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    nutrition = models.ForeignKey(RecipeAttributeLimit, on_delete=models.CASCADE)
    nutrition_name = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    class Meta:
        unique_together = ("recipe", "nutrition_name")


class RecipeRatios(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    nutrition_1 = models.ForeignKey(
        RecipeAttributeLimit,
        on_delete=models.CASCADE,
        related_name="nutrition_1_ratios",
    )
    nutrition_1_name = models.CharField(max_length=255)
    nutrition_2 = models.ForeignKey(
        RecipeAttributeLimit,
        on_delete=models.CASCADE,
        related_name="nutrition_2_ratios",
    )
    nutrition_2_name = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
