# Generated by Django 4.1.5 on 2023-10-09 05:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "ingredients",
            "0008_rename_material_1_name_reciperatios_nutrition_1_name_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="reciperatios",
            name="value",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
