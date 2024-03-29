# Generated by Django 4.1.5 on 2023-10-09 05:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ingredients", "0009_reciperatios_value"),
    ]

    operations = [
        migrations.CreateModel(
            name="BestRecipeNutrition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nutrition_name", models.CharField(max_length=255)),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=5,
                        verbose_name="percentage",
                    ),
                ),
                (
                    "nutrition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ingredients.reciperawmaterial",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ingredients.recipe",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("recipe", "nutrition_name")},
            },
        ),
    ]
