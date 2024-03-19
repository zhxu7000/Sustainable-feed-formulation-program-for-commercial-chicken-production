from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import RecipeAttributeLimit, Recipe  # Import your models
from django.views.decorators.csrf import csrf_exempt


# @login_required(login_url="/login/")
@csrf_exempt
def recipe_attribute_limit_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        limit_id = request.POST.get("limit_id")
        recipe_id = request.POST.get("recipe_id")
        attribute_name = request.POST.get("attribute_name")
        min_value = request.POST.get("min_value")
        max_value = request.POST.get("max_value")

        try:
            if action == "create":
                recipe = Recipe.objects.get(id=recipe_id)
                ## print(recipe)
                attribute_limit_data = RecipeAttributeLimit.objects.create(
                    user=current_user,
                    recipe=recipe,
                    attribute_name=attribute_name,
                    min_value=min_value,
                    max_value=max_value,
                )
                object_data = model_to_dict(attribute_limit_data)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "read":
                attribute_limit_data = RecipeAttributeLimit.objects.filter(
                    recipe_id=recipe_id
                )
                ## print("配方营养需求", attribute_limit_data.values())
                data_list = list(attribute_limit_data.values())
                return JsonResponse({"status": "success", "data": data_list})

            elif action == "update":
                attribute_name = request.POST.get("attribute_name")
                min_value = request.POST.get("min_value")
                max_value = request.POST.get("max_value")
                ## print(limit_id)
                recipe_attribute_limit = RecipeAttributeLimit.objects.get(id=limit_id)
                recipe_attribute_limit.min_value = min_value
                recipe_attribute_limit.max_value = max_value
                recipe_attribute_limit.attribute_name = attribute_name
                recipe_attribute_limit.save()
                object_data = model_to_dict(recipe_attribute_limit)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "delete":
                recipe_attribute_limit = RecipeAttributeLimit.objects.get(id=limit_id)
                recipe_attribute_limit.delete()
                object_data = model_to_dict(recipe_attribute_limit)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "RecipeAttributeLimit or related objects do not exist",
                }
            )
        except IntegrityError as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})

    else:
        return JsonResponse(
            {
                "status": "error",
                "message": "Runtime error",
            }
        )
