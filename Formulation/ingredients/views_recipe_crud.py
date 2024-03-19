from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import (
    Recipe,
    RecipeAttributeLimit,
    RecipeRawMaterial,
    MaterialAttributeValue,
)
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


# @login_required(login_url="/login/")
@csrf_exempt
def recipe_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        recipe_id = request.POST.get("recipe_id")
        recipe_name = request.POST.get("recipe_name")
        ## print("user", current_user)

        try:
            if action == "create":
                id = request.POST.get("user_id")
                ## print(id)
                if id != None:
                    current_user = User.objects.get(id=id)
                with transaction.atomic():
                    recipe_data = Recipe.objects.create(
                        user=current_user, name=recipe_name
                    )
                    ## print(recipe_data)
                    object_data = model_to_dict(recipe_data)
                    ## print(object_data)

                    #
                    admin = User.objects.get(id=1)
                    for recipeAttributeObj in RecipeAttributeLimit.objects.filter(
                        user=admin, recipe_id=1
                    ):
                        attribute_limit_data = RecipeAttributeLimit.objects.create(
                            user=current_user,
                            recipe=recipe_data,
                            attribute_name=recipeAttributeObj.attribute_name,
                            min_value=recipeAttributeObj.min_value,
                            max_value=recipeAttributeObj.max_value,
                        )
                    for MaterialObj in RecipeRawMaterial.objects.filter(
                        user=admin, recipe_id=1
                    ):
                        recipe_raw_material = RecipeRawMaterial.objects.create(
                            user=current_user,
                            recipe=recipe_data,
                            material_name=MaterialObj.material_name,
                            price_per_kg=MaterialObj.price_per_kg,
                            max_percentage=MaterialObj.max_percentage,
                            min_percentage=MaterialObj.min_percentage,
                            min_weight_kg_per_ton=MaterialObj.min_weight_kg_per_ton,
                            max_weight_kg_per_ton=MaterialObj.max_weight_kg_per_ton,
                        )

                    recipe_raw_material_list = RecipeRawMaterial.objects.filter(
                        recipe=recipe_data, user=current_user
                    )
                    for NewMaterialObj in recipe_raw_material_list:
                        templateObj = RecipeRawMaterial.objects.get(
                            user=admin,
                            recipe_id=1,
                            material_name=NewMaterialObj.material_name,
                        )
                        for NutritionObj in MaterialAttributeValue.objects.filter(
                            user=admin, recipe_id=1, raw_material=templateObj
                        ):
                            material_attribute = MaterialAttributeValue.objects.create(
                                user=current_user,
                                recipe=recipe_data,
                                raw_material=NewMaterialObj,
                                attribute_name=NutritionObj.attribute_name,
                                value=NutritionObj.value,
                            )
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "update":
                recipe = Recipe.objects.get(id=recipe_id, user=current_user)
                recipe.name = recipe_name
                recipe.save()
                object_data = model_to_dict(recipe)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "delete":
                recipe = Recipe.objects.get(id=recipe_id, user=current_user)
                recipe.delete()
                object_data = model_to_dict(recipe)
                ## print(object_data)
                return JsonResponse({"status": "success", "data": object_data})

            elif action == "get":
                recipe = Recipe.objects.filter(user=current_user)
                ## print("in", recipe)
                data_list = list(recipe.values())
                return JsonResponse({"status": "success", "data": data_list})

            elif action == "get_first":
                recipe = Recipe.objects.filter(user=current_user).first()
                if recipe != None:
                    object_data = model_to_dict(recipe)
                    return JsonResponse({"status": "success", "data": object_data})
                return JsonResponse({"status": "error", "data": recipe})

        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "Recipe does not exist"})
        """ except IntegrityError as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})
 """
    else:
        return render(request, "recipe_crud.html")
