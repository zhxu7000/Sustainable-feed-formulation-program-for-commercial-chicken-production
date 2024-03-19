""" from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import RawMaterial, Recipe  # Import your models

@login_required(login_url='/login/')
def raw_material_crud(request):
    current_user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        recipe_name = request.POST.get('recipe_name')

        try:
            recipe = Recipe.objects.get(name=recipe_name, user=current_user)

            if action == 'create':
                RawMaterial.objects.create(
                    user=current_user,
                    recipe=recipe,
                    name=name
                )
                return JsonResponse({'status': 'success', 'message': 'Successfully created'})

            elif action == 'read':
                material = RawMaterial.objects.get(name=name, user=current_user)
                return JsonResponse({'status': 'success', 'data': {'name': material.name}})

            elif action == 'update':
                material = RawMaterial.objects.get(name=name, user=current_user)
                material.name = request.POST.get('new_name')
                material.save()
                return JsonResponse({'status': 'success', 'message': 'Successfully updated'})

            elif action == 'delete':
                material = RawMaterial.objects.get(name=name, user=current_user)
                material.delete()
                return JsonResponse({'status': 'success', 'message': 'Successfully deleted'})

        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material or related objects do not exist'})

    else:
        return render(request, 'raw_material_crud.html') """
