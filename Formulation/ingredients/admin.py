from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    MaterialAttributeValue,
    Recipe,
    RecipeRawMaterial,
    RecipeAttributeLimit,
)


# MaterialAttributeValue
class MaterialAttributeValueResource(resources.ModelResource):
    class Meta:
        model = MaterialAttributeValue


@admin.register(MaterialAttributeValue)
class MaterialAttributeValueAdmin(ImportExportModelAdmin):
    resource_class = MaterialAttributeValueResource
    list_display = ["raw_material", "user", "recipe", "value", "selected"]
    search_fields = [
        "raw_material__name",
        "user__username",
        "recipe__name",
        "attribute__name",
        "selected",
    ]
    list_filter = ["raw_material", "user", "recipe", "selected"]


# Recipe
class RecipeResource(resources.ModelResource):
    class Meta:
        model = Recipe


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    resource_class = RecipeResource
    list_display = ["name", "user", "selected"]
    search_fields = ["name", "user__username", "selected"]
    list_filter = ["user", "selected"]


# RecipeRawMaterial
class RecipeRawMaterialResource(resources.ModelResource):
    class Meta:
        model = RecipeRawMaterial


@admin.register(RecipeRawMaterial)
class RecipeRawMaterialAdmin(ImportExportModelAdmin):
    resource_class = RecipeRawMaterialResource
    list_display = [
        "material_name",
        "user",
        "recipe",
        "max_percentage",
        "min_percentage",
        "min_weight_kg_per_ton",
        "max_weight_kg_per_ton",
        "selected",
    ]
    search_fields = ["raw_material__name", "user__username", "recipe__name", "selected"]
    list_filter = ["material_name", "user", "recipe", "selected"]


# RecipeAttributeLimit
class RecipeAttributeLimitResource(resources.ModelResource):
    class Meta:
        model = RecipeAttributeLimit


@admin.register(RecipeAttributeLimit)
class RecipeAttributeLimitAdmin(ImportExportModelAdmin):
    resource_class = RecipeAttributeLimitResource
    list_display = [
        "recipe",
        "user",
        "attribute_name",
        "min_value",
        "max_value",
        "selected",
    ]
    search_fields = ["recipe__name", "user__username", "attribute__name", "selected"]
    list_filter = ["recipe", "user", "attribute_name", "selected"]
