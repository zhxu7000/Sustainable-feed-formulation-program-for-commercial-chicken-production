from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import (
    MaterialAttributeValue,
    Recipe,
    RecipeRawMaterial,
)  # Import your models
from django.views.decorators.csrf import csrf_exempt


# @login_required(login_url="/login/")
@csrf_exempt
def material_attribute_value_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        attribute_id = request.POST.get("attribute_id")
        recipe_id = request.POST.get("recipe_id")
        material_id = request.POST.get("material_id")
        attribute_name = request.POST.get("attribute_name")
        value = request.POST.get("value")

        try:
            if action == "create":
                recipe = Recipe.objects.get(id=recipe_id)
                material_attribute = MaterialAttributeValue.objects.create(
                    user=current_user,
                    recipe=recipe,
                    raw_material_id=material_id,
                    attribute_name=attribute_name,
                    value=value,
                )
                object_data = model_to_dict(material_attribute)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "read":
                ## print(material_id, current_user)
                material_nutrition_list = MaterialAttributeValue.objects.filter(
                    raw_material_id=material_id, user=current_user
                )
                material_name = RecipeRawMaterial.objects.get(
                    id=material_id
                ).material_name
                ## print("成分营养", material_nutrition_list.values())
                data_list = list(material_nutrition_list.values())
                return JsonResponse(
                    {
                        "status": "success",
                        "data": data_list,
                        "material_name": material_name,
                    }
                )

            elif action == "update":
                ## print(request.POST)
                material = MaterialAttributeValue.objects.get(
                    id=attribute_id, user=current_user
                )
                material.attribute_name = attribute_name
                material.value = value
                material.save()
                object_data = model_to_dict(material)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "delete":
                material = MaterialAttributeValue.objects.get(
                    id=attribute_id, user=current_user
                )
                material.delete()
                object_data = model_to_dict(material)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Material or related objects do not exist",
                }
            )
        except IntegrityError as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})

    else:
        return render(request, "raw_material_crud.html")
