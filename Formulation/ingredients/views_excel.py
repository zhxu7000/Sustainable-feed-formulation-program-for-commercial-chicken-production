from io import BytesIO
from .models import (
    MaterialAttributeValue,
    Recipe,
    RecipeRawMaterial,
    RecipeAttributeLimit,
)

from django.http import FileResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import pandas as pd
from django.forms.models import model_to_dict
from django.contrib.auth.models import User

@login_required
def import_excel_view(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # Extract the uploaded Excel file using the correct name 'excel_file'
    uploaded_file = request.FILES.get('excel_file')
    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "No file uploaded."})

    # Load Excel file into pandas
    try:
        xls = pd.ExcelFile(uploaded_file)
    except Exception as e:
        print(f"Error loading excel file: {e}")
        return JsonResponse({"status": "error", "message": f"Error reading Excel file: {str(e)}"})

    current_user = request.user

    # Import data based on sheet names
    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name)
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            return JsonResponse({"status": "error", "message": f"Error reading sheet {sheet_name}: {str(e)}"})

        print(f"Processing sheet: {sheet_name}")

        # Handle each sheet as before but with more error handling
        try:
            if sheet_name == "Recipes":
                for _, row in df.iterrows():
                    data = row.to_dict()

                    # Get the User instance based on the ID in the data
                    user_id = data.get('user')
                    try:
                        user_instance = User.objects.get(pk=user_id)
                    except User.DoesNotExist:
                        print(f"User with ID {user_id} does not exist. Skipping this row.")
                        continue

                    data['user'] = user_instance
                    Recipe.objects.update_or_create(user=current_user, name=data['name'], defaults=data)

            elif sheet_name.startswith("Recipe_"):  # The specific name of the recipe
                recipe_name = sheet_name.split('_')[1]
                try:
                    recipe = Recipe.objects.get(name=recipe_name, user=current_user)
                except Recipe.DoesNotExist:
                    continue

                for _, row in df.iterrows():
                    data = row.to_dict()
                    RecipeRawMaterial.objects.update_or_create(user=current_user, recipe=recipe, material_name=data['material_name'], defaults=data)

            elif sheet_name == "MaterialAttributeValues":
                for _, row in df.iterrows():
                    data = row.to_dict()
                    try:
                        # Change 'recipe' to 'recipe_id' and 'raw_material' to 'raw_material_id'
                        recipe = Recipe.objects.get(id=data['recipe_id'], user=current_user)
                        raw_material = RecipeRawMaterial.objects.get(id=data['raw_material_id'])
                        MaterialAttributeValue.objects.update_or_create(user=current_user, recipe=recipe,
                                                                        raw_material=raw_material,
                                                                        attribute_name=data['attribute_name'],
                                                                        defaults=data)
                    except ObjectDoesNotExist:
                        print(
                            f"Error: Recipe with ID {data['recipe_id']} or Raw Material with ID {data['raw_material_id']} does not exist.")
                        continue

            elif sheet_name == "RecipeAttributeLimits":
                for _, row in df.iterrows():
                    data = row.to_dict()
                    try:
                        # Change 'recipe' to 'recipe_id'
                        recipe = Recipe.objects.get(id=data['recipe_id'], user=current_user)

                        RecipeAttributeLimit.objects.update_or_create(user=current_user, recipe=recipe, attribute_name=data['attribute_name'], defaults=data)
                    except ObjectDoesNotExist:
                        print(f"Error: Recipe with ID {data['recipe_id']} does not exist.")
                        continue


        except ObjectDoesNotExist as e:
            print(f"Object not found error for sheet {sheet_name}: {e}")
            return JsonResponse({"status": "error", "message": f"Object not found error for sheet {sheet_name}: {str(e)}"})
        except IntegrityError as e:
            print(f"Integrity error for sheet {sheet_name}: {e}")
            return JsonResponse({"status": "error", "message": f"Integrity error for sheet {sheet_name}: {str(e)}"})
        except Exception as e:
            print(f"General error for sheet {sheet_name}: {e}")
            return JsonResponse({"status": "error", "message": f"General error for sheet {sheet_name}: {str(e)}"})

    return JsonResponse({"status": "success", "message": "Data imported successfully."})

@login_required
def export_excel_view(request):
    current_user = request.user
    recipe_id = request.GET.get('recipe_id')

    if not recipe_id:
        return JsonResponse({"status": "error", "message": "Recipe ID is required."})

    try:
        recipe = Recipe.objects.get(id=recipe_id, user=current_user)
    except Recipe.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Recipe not found."})

    if request.method == "GET":
        try:
            output = BytesIO()
            username = current_user.username
            filename = f"{username}_{recipe.name}_database.xlsx"

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

                # 导出 Recipe 表
                df_recipes = pd.DataFrame.from_records([model_to_dict(recipe)])
                df_recipes.to_excel(writer, sheet_name='Recipes', index=False)

                # 导出 RecipeRawMaterial 表
                materials = RecipeRawMaterial.objects.filter(user=request.user, recipe=recipe).values()
                df_materials = pd.DataFrame.from_records(materials)
                df_materials.to_excel(writer, sheet_name=f'Recipe_{recipe.name}', index=False)

                # 导出 MaterialAttributeValue 表
                attributes = MaterialAttributeValue.objects.filter(user=request.user, recipe=recipe).values()
                df_attributes = pd.DataFrame.from_records(attributes)
                df_attributes.to_excel(writer, sheet_name='MaterialAttributeValues', index=False)

                # 导出 RecipeAttributeLimit 表
                attribute_limits = RecipeAttributeLimit.objects.filter(user=request.user, recipe=recipe).values()
                df_attribute_limits = pd.DataFrame.from_records(attribute_limits)
                df_attribute_limits.to_excel(writer, sheet_name='RecipeAttributeLimits', index=False)

            output.seek(0)
            response = FileResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response

        except Exception as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "message": error_message})

    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})


