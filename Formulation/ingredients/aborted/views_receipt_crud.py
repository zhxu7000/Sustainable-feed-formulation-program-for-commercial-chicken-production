""" from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import Receipt, Recipe  # Import your models

@login_required(login_url='/login/')
def receipt_crud(request):
    current_user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        recipe_name = request.POST.get('recipe_name')
        total_tones = request.POST.get('total_tones')

        try:
            recipe = Recipe.objects.get(name=recipe_name, user=current_user)

            if action == 'create':
                Receipt.objects.create(
                    user=current_user,
                    recipe=recipe,
                    total_tones=total_tones
                )
                return JsonResponse({'status': 'success', 'message': 'Successfully created'})

            elif action == 'read':
                receipt = Receipt.objects.get(recipe=recipe, user=current_user)
                return JsonResponse({'status': 'success', 'data': {'total_tones': str(receipt.total_tones)}})

            elif action == 'update':
                receipt = Receipt.objects.get(recipe=recipe, user=current_user)
                receipt.total_tones = request.POST.get('new_total_tones')
                receipt.save()
                return JsonResponse({'status': 'success', 'message': 'Successfully updated'})

            elif action == 'delete':
                receipt = Receipt.objects.get(recipe=recipe, user=current_user)
                receipt.delete()
                return JsonResponse({'status': 'success', 'message': 'Successfully deleted'})

        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Receipt or related objects do not exist'})

    else:
        return render(request, 'receipt_crud.html') """
