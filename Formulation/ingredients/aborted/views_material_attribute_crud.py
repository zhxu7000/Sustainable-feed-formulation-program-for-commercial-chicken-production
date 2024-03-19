""" from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import MaterialAttribute


@login_required(login_url="/login/")
def material_attribute_crud(request):
    current_user = request.user
    if request.method == "POST":
        action = request.POST.get("action")
        name = request.POST.get("name")
        description = request.POST.get("description")

        try:
            if action == "create":
                MaterialAttribute.objects.create(
                    user=current_user, name=name, description=description
                )
                return JsonResponse(
                    {"status": "success", "message": "Successfully created"}
                )

            elif action == "read":
                attribute = MaterialAttribute.objects.get(name=name, user=current_user)
                return JsonResponse(
                    {
                        "status": "success",
                        "data": {
                            "name": attribute.name,
                            "description": attribute.description,
                        },
                    }
                )

            elif action == "update":
                attribute = MaterialAttribute.objects.get(name=name, user=current_user)
                attribute.name = request.POST.get("new_name")
                attribute.description = request.POST.get("new_description")
                attribute.save()
                return JsonResponse(
                    {"status": "success", "message": "Successfully updated"}
                )

            elif action == "delete":
                attribute = MaterialAttribute.objects.get(name=name, user=current_user)
                attribute.delete()
                return JsonResponse(
                    {"status": "success", "message": "Successfully deleted"}
                )

        except ObjectDoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Attribute does not exist"}
            )

    else:
        return render(request, "material_attribute_crud.html") """
