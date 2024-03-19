from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.platypus import Image as RLImage
from PIL import Image as PILImage
from decimal import Decimal
from .models import (
    UserRegisterForm,
)
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.contrib.auth.models import User
import hashlib
from django.contrib.auth import login, authenticate
from django.db import transaction
from .models import (
    BestRecipe,
    BestRecipeNutrition,
)
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, lpSum, value
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import FileResponse, JsonResponse
from .models import (
    Recipe,
    RecipeRawMaterial,
    MaterialAttributeValue,
    RecipeAttributeLimit,
)
from django.core.exceptions import ObjectDoesNotExist
import requests
import traceback  
from io import BytesIO
from decimal import Decimal
from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import traceback
from reportlab.lib.colors import Color, black, beige
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import PageBreak
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json
def encrypt_username(username):
    return hashlib.sha256(username.encode()).hexdigest()


def set_lp_variables(materials):
    print("Setting LP Variables")
    var_dict = {}
    for material in materials:
        var_name = f"percentage_{material.material_name}"
        var_dict[material] = LpVariable(var_name, 0, 100)
        ## print(f"Var for {material.material_name}: {var_name}")
    return var_dict


def set_objective_function(prob, var_dict, materials):
    print("Setting Objective Function")
    costs = [
        float(material.price_per_kg) * 1000 * var_dict[material]
        for material in materials
    ]
    prob += lpSum(costs)


def set_material_constraints(prob, var_dict, materials):
    print("Setting Material Constraints")
    for material in materials:
        prob += var_dict[material] >= float(material.min_percentage)
        prob += var_dict[material] <= float(material.max_percentage)
        ## print(f"Constraints for {material.material_name}: [{float(material.min_percentage)}, {float(material.max_percentage)}]")


def set_attribute_constraints(prob, var_dict, current_user, materials, recipe_attribute_limits):
    print("Setting Attribute Constraints")
    for ral in recipe_attribute_limits:
        attribute_contributions = []
        ## print(f"Processing attribute: {ral.attribute_name}")
        for material in materials:
            attribute_value = MaterialAttributeValue.objects.filter(
                user=current_user,
                raw_material=material,
                attribute_name=ral.attribute_name,
            ).first()

            if attribute_value:
                # 这里我们考虑了原材料在混合中的百分比
                contribution = var_dict[material] * float(attribute_value.value) / 100
                attribute_contributions.append(contribution)
                ## print(f"{material.material_name} contribution to {ral.attribute_name}: {contribution}")

        # 这里我们设置了整个配方的属性值的约束
        prob += lpSum(attribute_contributions) >= float(ral.min_value/10)
        prob += lpSum(attribute_contributions) <= float(ral.max_value/10)


def calculate_nutrition_values(current_user, materials, var_dict):
    """
    Calculate the nutrition values for the resulting mix based on the optimal mix percentages.
    """
    nutrition_values = {}
    for material in materials:
        nutrition_entries = MaterialAttributeValue.objects.filter(
            user=current_user, raw_material=material
        )
        for entry in nutrition_entries:
            if entry.attribute_name not in nutrition_values:
                nutrition_values[entry.attribute_name] = 0
            nutrition_values[entry.attribute_name] += (
                float(entry.value) * var_dict[material].varValue / 100
            )
    return nutrition_values


def find_optimal_mix(current_user, recipe_id):
    print("Finding Optimal Mix")
    prob = LpProblem("OptimalFeedMix", LpMinimize)

    current_user = User.objects.get(username=current_user)
    materials = RecipeRawMaterial.objects.filter(user=current_user, recipe_id=recipe_id)
    ## print(f"Materials: {[m.material_name for m in materials]}")

    var_dict = set_lp_variables(materials)
    set_objective_function(prob, var_dict, materials)
    set_material_constraints(prob, var_dict, materials)

    recipe_attribute_limits = RecipeAttributeLimit.objects.filter(
        user=current_user, recipe_id=recipe_id
    )
    set_attribute_constraints(
        prob, var_dict, current_user, materials, recipe_attribute_limits
    )

    prob += lpSum(var_dict.values()) == 100

    print("Solving LP problem")
    prob.solve()
    print(prob)

    material_percentages = {}
    if LpStatus[prob.status] == "Optimal":
        for material in materials:
            material_percentages[material.material_name] = var_dict[material].varValue

        nutrition_values = calculate_nutrition_values(
            current_user, materials, var_dict
        )

        # 在函数的末尾，计算整个配方的营养物质含量
        total_nutrition_values = {}
        for material in materials:
            nutrition_entries = MaterialAttributeValue.objects.filter(
                user=current_user, raw_material=material
            )
            for entry in nutrition_entries:
                if entry.attribute_name not in total_nutrition_values:
                    total_nutrition_values[entry.attribute_name] = 0
                total_nutrition_values[entry.attribute_name] += (
                    float(entry.value) * var_dict[material].varValue / 100  # 除以100是因为varValue是百分比
                )

        return {
            "msg": "Optimal solution found and saved!",
            "data": material_percentages,
            "materials": list(materials.values()),
            "total_cost": value(prob.objective),
            "nutrition_values": nutrition_values,             # 这是每个原材料的营养物质值
            "total_nutrition_values": total_nutrition_values  # 这是整个配方的营养物质值
        }
    else:
        print(f"LP Problem Status: {LpStatus[prob.status]}")
        return {"msg": "No optimal solution found!", "data": None}


@csrf_exempt
def calculate_view(request):
    if request.method == "POST":
        recipe_id = request.POST.get("recipe_id")
        ## print("calculate", request.user, recipe_id)
        result = find_optimal_mix(
            request.user, recipe_id
        )  # Assuming find_optimal_mix is modified to handle errors
        # result = 1
        ## print("calculate", result)
        if result["msg"] == "Optimal solution found and saved!":
            encrypted_username = encrypt_username(request.user.username)
            data_list = save_best_recipe(request.user, recipe_id, result["data"])

            # Handle the exception here
            try:
                nutrition_list = save_nutrition(
                    request.user, recipe_id, result["nutrition_values"]
                )
            except RecipeAttributeLimit.DoesNotExist:
                # Provide default values
                nutrition_list = {
                    "min_value": 0.00,
                    "max_value": 999.99
                }

            return JsonResponse(
                {
                    "status": "success",
                    "data": data_list,
                    "ratios": nutrition_list,
                    "message": "Optimal solution found and saved!",
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "No optimal solution found!"}
            )
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"})


def save_best_recipe(user, recipe_id, data):
    print("saving")
    recipe = Recipe.objects.get(id=recipe_id)
    BestRecipe.objects.filter(
        user=user,
        recipe=recipe,
    ).delete()
    total_cost = 0
    for key, value in data.items():
        print(key, value)
        material = RecipeRawMaterial.objects.get(
            user=user, recipe=recipe, material_name=key
        )
        defaults = {"value": value}
        BestRecipe.objects.update_or_create(
            user=user,
            recipe=recipe,
            material=material,
            material_name=key,
            defaults=defaults,
        )
        material_cost = Decimal(material.price_per_kg) * Decimal(value)
        total_cost = total_cost + material_cost

    best_recipe_list = BestRecipe.objects.filter(user=user, recipe=recipe)
    recipe.total_cost_pre = recipe.total_cost
    recipe.total_cost = total_cost
    recipe.save()
    data_list = list(best_recipe_list.values())
    return data_list



def save_nutrition(user, recipe_id, data):
    print("saving ratios")
    recipe = Recipe.objects.get(id=recipe_id)
    BestRecipeNutrition.objects.filter(
        user=user,
        recipe=recipe,
    ).delete()
    for key, value in data.items():
        print(key, value)
        nutrition = RecipeAttributeLimit.objects.get(
            user=user, recipe=recipe, attribute_name=key
        )
        defaults = {"value": value}
        BestRecipeNutrition.objects.update_or_create(
            user=user,
            recipe=recipe,
            nutrition=nutrition,
            nutrition_name=key,
            defaults=defaults,
        )

    best_recipe_list = BestRecipeNutrition.objects.filter(user=user, recipe=recipe)
    data_list = list(best_recipe_list.values())
    return data_list


def set_tonne(request):
    if request.method == "POST":
        action = request.POST.get("action")
        recipe_id = request.POST.get("recipe_id")

        try:
            if action == "create":
                tonne_value = request.POST.get("tonne")
                if not tonne_value:
                    return JsonResponse({"status": "error", "message": "Tonne value is missing."})

                # Convert tonne value to Decimal
                tonne_value = Decimal(tonne_value)
                ## print(f"Setting tonne value to: {tonne_value}")

                # Fetch the recipe
                recipe = Recipe.objects.get(id=recipe_id)
                # Update the tonne value for the recipe
                recipe.tonne = tonne_value
                recipe.save()

                # Fetch the recipe again to ensure the value is saved
                saved_recipe = Recipe.objects.get(id=recipe_id)
                ## print(f"Saved tonne value in database: {saved_recipe.tonne}")

                return JsonResponse({"status": "success", "tonne": str(tonne_value)})

        except Recipe.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Recipe does not exist."})
        except Exception as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "message": error_message})
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"})


@csrf_exempt
def get_material_cost_weight_and_percentage(request):
    print("---- Starting get_material_cost_weight_and_percentage ----")
    
    recipe_id = request.GET.get("recipe_id")
    print(f"Recipe ID: {recipe_id}")

    if not recipe_id:
        return JsonResponse({"status": "error", "message": "Recipe ID is missing."})

    try:
        result = find_optimal_mix(request.user.username, recipe_id)
        ## print(f"Optimal Mix Result: {result}")

        if result["msg"] != "Optimal solution found and saved!":
            return JsonResponse({"status": "error", "message": "No optimal solution found!"})

        recipe = get_object_or_404(Recipe, id=recipe_id)
        tonne = recipe.tonne
        ## print(f"Recipe: {recipe}, Tonne: {tonne}")

        materials = RecipeRawMaterial.objects.filter(user=request.user, recipe_id=recipe_id)
        material_data = []

        for material in materials:
            optimal_percentage = result['data'].get(material.material_name, 0) / 100  
            weight = Decimal(tonne) * Decimal(optimal_percentage)
            total_cost = Decimal(material.price_per_kg) * weight * Decimal(1000)  

            ## print(f"Material: {material.material_name}")
            ## print(f"Optimal Percentage: {optimal_percentage}")
            ## print(f"Weight: {weight}")
            ## print(f"Total Cost: {total_cost}")

            material_data.append({
                "material_name": material.material_name,
                "optimal_percentage": optimal_percentage, 
                "weight": f"{weight:.2f} tonne",
                "total_cost": f"${total_cost:.2f}"
            })
        print(material_data)
        return JsonResponse({
            "status": "success",
            "data": material_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({
            "status": "error",
            "message": "An unexpected error occurred. Please try again later."
        })



@login_required
def download_pdf_view(request):
    if request.method == "GET":
        tonne_purchased_list = []
        material_names_list = []
        material_costs = []
        try:
            user = request.user
            buffer = BytesIO()

            
            # Get the recipe_id from the request
            recipe_id = request.GET.get('recipe_id')
            if not recipe_id:
                return JsonResponse({"status": "error", "message": "Recipe ID is missing."})

            # Fetch the specific recipe using the recipe_id
            recipe = Recipe.objects.get(id=recipe_id, user=user)

            # Initialize PDF
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            elements = []


            try:
                # 从URL下载图片
                image_url = "https://s2.loli.net/2023/10/16/jbfSighF6K83JsW.jpg"
                response = requests.get(image_url)
                image_data = response.content
                
                # 使用ReportLab的Image类创建一个图片对象
                img = Image(BytesIO(image_data))
                
                # 调整图片大小，如果需要的话
                # 例如：缩放为4x4英寸大小
                img.drawHeight = 1 * inch
                img.drawWidth = 3 * inch

                # 添加图片到PDF文档
                elements.append(img)

                # 在图片和文字之间增加两行换行符号
                elements.append(Spacer(1, 24))  # Assuming 12 units per line, so 24 units for 2 lines

            except Exception as e:
                print(f"Error embedding the image: {str(e)}")



            # Add title
            title = Paragraph("Materials and Recipe Report", styles["Heading1"])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Process the specific recipe
            elements.append(Paragraph(f"Recipe: {recipe.name}", styles["Heading2"]))

            elements.append(
                    Paragraph(f"Tonne for recipe {recipe.name}: {recipe.tonne}", styles["Heading3"]))  # 打印配方的吨数

            # Call find_optimal_mix to get total nutrition values and optimal percentages
            result = find_optimal_mix(request.user.username, recipe.id)

            # Fetch materials for the recipe
            materials = RecipeRawMaterial.objects.filter(user=user, recipe=recipe)
            total_cost = 0


            for material in materials:
                try:
                    # Calculate Tonne Purchased for the material
                    optimal_percentage = Decimal(
                        result['data'].get(material.material_name, 0) / 100)  # Convert percentage to a fraction
                    tonne_purchased = Decimal(recipe.tonne) * optimal_percentage

                    # Calculate Total Cost for Material
                    material_cost = Decimal(material.price_per_kg) * tonne_purchased * Decimal(
                        1000)  # Convert tonne to kg and multiply by price per kg

                    # Calculate Tonne Purchased for the material
                    optimal_percentage = Decimal(
                        result['data'].get(material.material_name, 0) / 100)  # Convert percentage to a fraction
                    tonne_purchased = Decimal(recipe.tonne) * optimal_percentage

                    tonne_purchased_list.append(tonne_purchased)
                    material_names_list.append(material.material_name)

                    # Calculate Total Cost for Material
                    material_cost = Decimal(material.price_per_kg) * tonne_purchased * Decimal(1000)
                    material_costs.append(material_cost)

                except Exception as e:
                    print(f"Error while calculating material_cost: {e}")
                    continue
                total_cost += material_cost
                data = [
                    ["Material Name", material.material_name],
                    ["Price per Kg", f"${material.price_per_kg}"],
                    ["Tonne Purchased", f"{tonne_purchased}"],  # Updated Tonne Purchased
                    ["Total Cost for Material", f"${material_cost}"],  # Updated Total Cost for Material
                    ["Min Percentage", f"{material.min_percentage}%"],
                    ["Max Percentage", f"{material.max_percentage}%"],
                    ["Min Weight (kg/ton)", material.min_weight_kg_per_ton],
                    ["Max Weight (kg/ton)", material.max_weight_kg_per_ton],
                    ["Optimal Percentage", f"{optimal_percentage * 100}%"]  # Convert fraction back to percentage
                ]
                try:
                    table = Table(data, colWidths=[200, 350])
                    table_style = TableStyle(
                        [
                            ('BACKGROUND', (0, 0), (1, 0), Color(230/255, 70/255, 38/255)),  # 橙色
                            ('TEXTCOLOR', (0, 0), (1, 0), black),  # 黑色、
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), beige),
                            ('GRID', (0, 0), (-1, -1), 1, black)

                        ]
                    )
                    table.setStyle(table_style)
 
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                    elements.append(PageBreak())
                except Exception as e:
                    return JsonResponse({"status": "error", "message": f"Error while setting table style: {str(e)}"})

            # Add total cost for the recipe
            elements.append(Paragraph(f"Total Cost for {recipe.name}: ${total_cost}", styles["Heading3"]))

            # Call find_optimal_mix to get total nutrition values
            total_nutrition_values = result.get("total_nutrition_values", {})

            # Display total nutrition values in the PDF
            for key, value in total_nutrition_values.items():
                data = [
                    ["Nutrition Name", key],
                    ["Total Value", value],
                ]
                table = Table(data, colWidths=[200, 350])
                table.setStyle(table_style)
                elements.append(table)
                elements.append(Spacer(1, 20))
            elements.append(PageBreak())
            # Fetch attribute values and limits for the materials in the recipe
            attribute_values = MaterialAttributeValue.objects.filter(user=user)
            for attribute in attribute_values:
                limits = RecipeAttributeLimit.objects.filter(
                    attribute_name=attribute.attribute_name, recipe=recipe
                ).first()
                data = [
                    ["Material", attribute.raw_material.material_name],# Add this line to display the material name
                    ["Attribute Name", attribute.attribute_name],
                    ["Value", attribute.value],
                    ["Min Value", limits.min_value if limits else "N/A"],
                    ["Max Value", limits.max_value if limits else "N/A"],
                ]

                table = Table(data, colWidths=[200, 350])
                table.setStyle(table_style)
                elements.append(table)
                elements.append(Spacer(1, 20))

            elements.append(PageBreak())
            # 创建并添加 "Total Cost Distribution" 饼图
            labels = material_names_list
            sizes = material_costs
            colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
            # 检查 sizes 和 labels 的长度是否匹配
            if len(sizes) != len(labels):
                return JsonResponse({"status": "error", "message": "Mismatch in sizes and labels length."})

            # 检查 sizes 是否为空
            if not sizes:
                return JsonResponse({"status": "error", "message": "Sizes list is empty."})

            try:
                plt.figure(figsize=(6, 4))
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title("Total Cost Distribution")

                # 保存饼图为图片
                img_buffer = BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                img = PILImage.open(img_buffer)
                img_width, img_height = img.size
                img_buffer.seek(0)  # 确保你回到了BytesIO对象的开始位置
                elements.append(RLImage(img_buffer, width=img_width, height=img_height))
                elements.append(Spacer(1, 20))

            except Exception as e:
                error_info = traceback.format_exc()
                print(error_info)  
                return JsonResponse({"status": "error", "message": f"Error while creating 'Total Cost Distribution' pie chart: {str(e)}", "detail": error_info})

            # 创建并添加 "Tonne Purchased Distribution" 饼图
            sizes = tonne_purchased_list

            # 检查 sizes 和 labels 的长度是否匹配
            if len(sizes) != len(labels):
                return JsonResponse({"status": "error", "message": "Mismatch in sizes and labels length."})

            # 检查 sizes 是否为空
            if not sizes:
                return JsonResponse({"status": "error", "message": "Sizes list is empty."})

            try:
                plt.figure(figsize=(6, 4))
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title("Tonne Purchased Distribution")

                # 保存饼图为图片
                img_buffer2 = BytesIO()
                plt.savefig(img_buffer2, format='png')
                img_buffer2.seek(0)
                img2 = PILImage.open(img_buffer2)
                img2 = img2.resize((img_width, img_height))
                img_buffer2.seek(0)  
                elements.append(RLImage(img_buffer2, width=img_width, height=img_height))
                elements.append(Spacer(1, 20))

            except Exception as e:
                error_info = traceback.format_exc()
                print(error_info)  
                return JsonResponse({"status": "error", "message": f"Error while creating 'Tonne Purchased Distribution' pie chart: {str(e)}", "detail": error_info})

            elements.append(PageBreak())
            # Fetch materials for the recipe
            materials = RecipeRawMaterial.objects.filter(user=user, recipe=recipe)
            for material in materials:
                try:
                    # 重新计算每个原材料的相关数据

                    # Calculate Tonne Purchased for the material
                    optimal_percentage = Decimal(result['data'].get(material.material_name, 0) / 100)  # Convert percentage to a fraction
                    tonne_purchased = Decimal(recipe.tonne) * optimal_percentage

                    # Calculate Total Cost for Material
                    material_cost = Decimal(material.price_per_kg) * tonne_purchased * Decimal(1000)
                    
                    # 添加抬头
                    receipt_title = Paragraph(f"Receipt for {material.material_name}", styles["Heading2"])
                    elements.append(receipt_title)
                    elements.append(Spacer(1, 12))

                    # Prepare data for the table
                    data = [
                        ["Material Name", material.material_name],
                        ["Price per Kg", f"${material.price_per_kg}"],
                        ["Tonne Purchased", f"{tonne_purchased}"],  # Updated Tonne Purchased
                        ["Total Cost for Material", f"${material_cost}"],  # Updated Total Cost for Material
                        ["Min Percentage", f"{material.min_percentage}%"],
                        ["Max Percentage", f"{material.max_percentage}%"],
                        ["Min Weight (kg/ton)", material.min_weight_kg_per_ton],
                        ["Max Weight (kg/ton)", material.max_weight_kg_per_ton],
                        ["Optimal Percentage", f"{optimal_percentage * 100}%"]  # Convert fraction back to percentage
                    ]

                    table = Table(data, colWidths=[200, 350])
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))

                    # 创建一个表来显示原材料的所有营养属性
                    data = [["Attribute Name", "Value"]]
                    
                    # 查询原材料的所有营养属性
                    nutrition_values = MaterialAttributeValue.objects.filter(user=user, raw_material=material)
                    
                    for attribute in nutrition_values:
                        data.append([attribute.attribute_name, attribute.value])
                        
                    table = Table(data, colWidths=[200, 350])
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                    elements.append(PageBreak())

                except Exception as e:
                    print(f"Error while processing material: {e}")
                    continue

            # Finally, build the document with all elements
            doc.build(elements)


            # Prepare response
            buffer.seek(0)
            response = FileResponse(buffer, content_type="application/pdf")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="materials_and_recipe_report.pdf"'
            return response

        except ObjectDoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Data or related objects for PDF generation do not exist.",
                }
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."})


@csrf_exempt
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                ## print("user", user.id)
                encrypted_username = encrypt_username(username)
                csrf_token = get_token(request)
                return JsonResponse(
                    {
                        "status": "success",
                        "redirect_url": f"/home/{encrypted_username}/",
                        "csrf_token": csrf_token,
                        "id": user.id,
                        "admin": user.is_superuser,
                    }
                )
            else:
                return JsonResponse(
                    {"status": "error", "message": "Invalid credentials"}
                )
        else:
            return JsonResponse({"status": "error", "message": "Invalid form data"})
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"})


@csrf_exempt
def user_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            print(new_user)
            object_data = forms.model_to_dict(new_user)
            print(object_data)
            csrf_token = get_token(request)
            return JsonResponse(
                {
                    "status": "success",
                    "csrf_token": csrf_token,
                    "id": new_user.id,
                }
            )

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Registration failed",
                    "form_errors": form.errors,
                }
            )
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"})


@csrf_exempt
def user_manage(request):
    if request.method == "POST":
        action = request.POST.get("action")

        try:
            if action == "read":
                user_list = User.objects.filter()
                data_list = list(
                    user_list.values("id", "username", "email", "last_login")
                )
                return JsonResponse({"status": "success", "data": data_list})
            if action == "delete":
                user_string = request.POST.get("user_list")
                csv_list = user_string.split(",")
                user_list = [int(item) for item in csv_list]
                print("userlist", user_list)
                with transaction.atomic():
                    for id in user_list:
                        print(id)
                        user = User.objects.get(id=id)
                        print(user)
                        user.delete()
                return JsonResponse({"status": "success", "data": user_list})

        except Exception as e:
            error_message = str(e)
            return JsonResponse({"status": "error", "data": error_message})


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=64)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
