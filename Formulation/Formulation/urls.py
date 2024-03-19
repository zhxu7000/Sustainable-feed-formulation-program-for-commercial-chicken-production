"""mynewproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from ingredients.views import (
    download_pdf_view,
    calculate_view,
    get_material_cost_weight_and_percentage,
    user_login,
    user_register,
    user_manage,
    set_tonne,
)

from ingredients.views_recipe_crud import recipe_crud
from ingredients.views_recipe_ratios_crud import recipe_ratio_crud
from ingredients.views_best_recipe_crud import best_recipe_crud
from ingredients.views_recipe_attribute_limit_crud import recipe_attribute_limit_crud
from ingredients.views_recipe_raw_material_crud import recipe_raw_material_crud
from ingredients.views_material_attribute_value_crud import (
    material_attribute_value_crud,
)
from django.urls import path, re_path
from ingredients.views_excel import import_excel_view, export_excel_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/download_pdf/", download_pdf_view, name="download_pdf"),
    path("api/calculate/", calculate_view, name="calculate"),
    path("api/set_tonne/", set_tonne, name="set_tonne"),
    path("api/login/", user_login, name="user_login"),
    path("api/register/", user_register, name="user_register"),
    path("api/user_manage/", user_manage, name="user_manage"),
    path("api/recipe_crud/", recipe_crud, name="recipe_crud"),
    path("api/best_recipe_crud/", best_recipe_crud, name="best_recipe_crud"),
    path("api/recipe_ratio_crud/", recipe_ratio_crud, name="recipe_ratio_crud"),
    path(
        "api/recipe_attribute_limit_crud/",
        recipe_attribute_limit_crud,
        name="recipe_attribute_limit_crud",
    ),
    path(
        "api/recipe_raw_material_crud/",
        recipe_raw_material_crud,
        name="recipe_raw_material_crud",
    ),
    path(
        "api/material_attribute_value_crud/",
        material_attribute_value_crud,
        name="material_attribute_value_crud",
    ),
    path("api/import_excel/", import_excel_view, name="import_excel_view"),
    path("api/export_excel/", export_excel_view, name="export_excel_view"),
    path('api/get_material_cost/', get_material_cost_weight_and_percentage, name='get_material_cost_weight_and_percentage'),
]
