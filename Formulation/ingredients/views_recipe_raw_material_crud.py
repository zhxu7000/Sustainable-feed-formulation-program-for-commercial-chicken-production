from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import RecipeRawMaterial, Recipe  # Import your models
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login/")
@csrf_exempt
def recipe_raw_material_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        material_id = request.POST.get("material_id")
        recipe_id = request.POST.get("recipe_id")
        material_name = request.POST.get("material_name")
        price_per_kg = request.POST.get("price")

        max_percentage = request.POST.get("max_percentage")
        min_percentage = request.POST.get("min_percentage")
        min_weight_kg_per_ton = request.POST.get("min_weight_kg_per_ton")
        max_weight_kg_per_ton = request.POST.get("max_weight_kg_per_ton")

        try:
            if action == "create":
                recipe = Recipe.objects.get(id=recipe_id)
                recipe_raw_material = RecipeRawMaterial.objects.create(
                    user=current_user,
                    recipe=recipe,
                    material_name=material_name,
                    price_per_kg=price_per_kg,
                    max_percentage=max_percentage,
                    min_percentage=min_percentage,
                    min_weight_kg_per_ton=min_weight_kg_per_ton,
                    max_weight_kg_per_ton=max_weight_kg_per_ton,
                )
                object_data = model_to_dict(recipe_raw_material)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "read":
                recipe = Recipe.objects.get(id=recipe_id)
                ## print(recipe_id, current_user)
                recipe_raw_material = RecipeRawMaterial.objects.filter(
                    recipe=recipe, user=current_user
                )
                ## print(recipe_raw_material.values())
                data_list = list(recipe_raw_material.values())
                return JsonResponse({"status": "success", "data": data_list})

            elif action == "get_first":
                recipe = Recipe.objects.get(id=recipe_id)
                recipe_raw_material = RecipeRawMaterial.objects.filter(
                    recipe=recipe, user=current_user
                ).first()
                if recipe_raw_material != None:
                    object_data = model_to_dict(recipe_raw_material)
                    return JsonResponse({"status": "success", "data": object_data})
                return JsonResponse({"status": "error", "data": recipe_raw_material})

            elif action == "update":
                recipe_raw_material = RecipeRawMaterial.objects.get(
                    id=material_id, user=current_user
                )
                print(request.POST)
                recipe_raw_material.material_name = material_name
                recipe_raw_material.max_percentage = max_percentage
                recipe_raw_material.min_percentage = min_percentage
                recipe_raw_material.min_weight_kg_per_ton = min_weight_kg_per_ton
                recipe_raw_material.max_weight_kg_per_ton = max_weight_kg_per_ton
                recipe_raw_material.price_per_kg = price_per_kg
                recipe_raw_material.save()
                object_data = model_to_dict(recipe_raw_material)
                # print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "delete":
                recipe_raw_material = RecipeRawMaterial.objects.get(
                    id=material_id, user=current_user
                )
                recipe_raw_material.delete()
                object_data = model_to_dict(recipe_raw_material)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "RecipeRawMaterial or related objects do not exist",
                }
            )
        except IntegrityError as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})
        except Exception as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})
        except RuntimeError as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})

    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
