from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import (
    RecipeRawMaterial,
    Recipe,
    BestRecipe,
    BestRecipeNutrition,
)  # Import your models
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login/")
@csrf_exempt
def best_recipe_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        recipe_id = request.POST.get("recipe_id")

        try:
            if action == "read":
                recipe = Recipe.objects.get(id=recipe_id)
                recipe_material_list = BestRecipe.objects.filter(
                    recipe=recipe, user=current_user
                )
                recipe_nutrition_list = BestRecipeNutrition.objects.filter(
                    recipe=recipe, user=current_user
                )
                price_pre = recipe.total_cost_pre
                price = recipe.total_cost
                object_data = list(recipe_material_list.values())
                nutrition_data = list(recipe_nutrition_list.values())
                ## print(object_data)
                return JsonResponse(
                    {
                        "status": "success",
                        "data": object_data,
                        "nutrition": nutrition_data,
                        "price": price,
                        "price_pre": price_pre,
                    }
                )

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

    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
