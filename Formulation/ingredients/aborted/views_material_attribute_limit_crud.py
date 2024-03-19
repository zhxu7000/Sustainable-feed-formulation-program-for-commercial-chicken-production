""" from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import MaterialAttributeLimit, MaterialAttribute, Recipe  # Import your models

@login_required(login_url='/login/')
def material_attribute_limit_crud(request):
    current_user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        recipe_name = request.POST.get('recipe_name')
        attribute_name = request.POST.get('attribute_name')
        description = request.POST.get('description')

        try:
            recipe = Recipe.objects.get(name=recipe_name, user=current_user)
            attribute = MaterialAttribute.objects.get(name=attribute_name, user=current_user)

            if action == 'create':
                MaterialAttributeLimit.objects.create(
                    user=current_user,
                    recipe=recipe,
                    attribute=attribute,
                    description=description
                )
                return JsonResponse({'status': 'success', 'message': 'Successfully created'})

            elif action == 'read':
                limit = MaterialAttributeLimit.objects.get(recipe=recipe, attribute=attribute, user=current_user)
                return JsonResponse({'status': 'success', 'data': {'description': limit.description}})

            elif action == 'update':
                limit = MaterialAttributeLimit.objects.get(recipe=recipe, attribute=attribute, user=current_user)
                limit.description = request.POST.get('new_description')
                limit.save()
                return JsonResponse({'status': 'success', 'message': 'Successfully updated'})

            elif action == 'delete':
                limit = MaterialAttributeLimit.objects.get(recipe=recipe, attribute=attribute, user=current_user)
                limit.delete()
                return JsonResponse({'status': 'success', 'message': 'Successfully deleted'})

        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Limit or related objects do not exist'})

    else:
        return render(request, 'material_attribute_limit_crud.html') """
