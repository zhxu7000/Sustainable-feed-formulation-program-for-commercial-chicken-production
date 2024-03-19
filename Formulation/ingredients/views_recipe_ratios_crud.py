from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import RecipeAttributeLimit, Recipe, RecipeRatios  # Import your models
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login/")
@csrf_exempt
def recipe_ratio_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        recipe_id = request.POST.get("recipe_id")
        nutrition1 = request.POST.get("nutrition1_id")
        nutrition2 = request.POST.get("nutrition2_id")
        ratio_id = request.POST.get("ratio_id")

        try:
            if action == "create":
                recipe = Recipe.objects.get(id=recipe_id)
                ## print(recipe, nutrition1, nutrition2)
                nutrition1_name = RecipeAttributeLimit.objects.get(
                    user=current_user, recipe=recipe, id=nutrition1
                ).attribute_name

                nutrition2_name = RecipeAttributeLimit.objects.get(
                    user=current_user, recipe=recipe, id=nutrition2
                ).attribute_name
                ## print(recipe, nutrition1_name, nutrition2_name)
                recipe_ratio = RecipeRatios.objects.create(
                    user=current_user,
                    recipe=recipe,
                    nutrition_1_id=nutrition1,
                    nutrition_2_id=nutrition2,
                    nutrition_1_name=nutrition1_name,
                    nutrition_2_name=nutrition2_name,
                )
                object_data = model_to_dict(recipe_ratio)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})
            elif action == "read":
                recipe = Recipe.objects.get(id=recipe_id)
                best_recipe_list = RecipeRatios.objects.filter(
                    recipe=recipe, user=current_user
                )
                object_data = list(best_recipe_list.values())
                ## print(object_data)
                return JsonResponse(
                    {
                        "status": "success",
                        "data": object_data,
                    }
                )
            elif action == "delete":
                ratio = RecipeRatios.objects.get(id=ratio_id)
                ratio.delete()
                object_data = model_to_dict(ratio)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Objects do not exist",
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
