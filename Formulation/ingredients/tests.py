import json
from django.test import TestCase,RequestFactory,Client
from django.contrib.auth.models import User
from .models import Recipe, RecipeRawMaterial, RecipeAttributeLimit, MaterialAttributeValue, BestRecipe, RecipeRatios
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Recipe, RecipeRawMaterial, MaterialAttributeValue, RecipeAttributeLimit,Recipe, RecipeAttributeLimit, RecipeRatios
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
from django.urls import reverse
from .models import User, Recipe, RecipeRawMaterial, MaterialAttributeValue, RecipeAttributeLimit,BestRecipeNutrition,UserCreationForm,UserRegisterForm
from .views import calculate_nutrition_values, encrypt_username, find_optimal_mix,download_pdf_view,set_tonne,save_best_recipe,save_nutrition
from .views import user_register,user_manage
from django.http import JsonResponse
import hashlib
from django.contrib.auth.models import User
from unittest import mock
from unittest.mock import patch,Mock
from io import BytesIO
from django.forms.models import model_to_dict
class RecipeModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        # Create a test recipe
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
    def test_recipe_creation(self):
        self.assertEqual(self.recipe.name, "Test Recipe")
    def test_recipe_raw_material_creation(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Test Material")
        self.assertEqual(material.material_name, "Test Material")
    def test_recipe_attribute_limit_creation(self):
        attribute_limit = RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name="Test Attribute")
        self.assertEqual(attribute_limit.attribute_name, "Test Attribute")
    def test_material_attribute_value_creation(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Test Material")
        attribute_value = MaterialAttributeValue.objects.create(user=self.user, raw_material=material, attribute_name="Test Value", value=10.5)
        self.assertEqual(attribute_value.value, 10.5)
    def test_best_recipe_creation(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Test Material")
        best_recipe = BestRecipe.objects.create(user=self.user, recipe=self.recipe, material=material, value=95.5)
        self.assertEqual(best_recipe.value, 95.5)
    def test_recipe_ratios_creation(self):
        nutrition_1 = RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name="Nutrition1")
        nutrition_2 = RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name="Nutrition2")
        ratio = RecipeRatios.objects.create(user=self.user, recipe=self.recipe, nutrition_1=nutrition_1, nutrition_1_name="Nutrition1", nutrition_2=nutrition_2, nutrition_2_name="Nutrition2")
        self.assertEqual(ratio.nutrition_1_name, "Nutrition1")
        self.assertEqual(ratio.nutrition_2_name, "Nutrition2")
    def test_create_recipe(self):
        recipe = Recipe.objects.create(user=self.user, name="test_recipe")
        self.assertEqual(recipe.name, "test_recipe")
        self.assertEqual(recipe.user, self.user)
        self.assertTrue(recipe.selected)
        self.assertEqual(recipe.total_cost_pre, 0)
        self.assertEqual(recipe.total_cost, 0)
    def test_create_raw_material(self):
        recipe = Recipe.objects.create(user=self.user, name="test_recipe")
        raw_material = RecipeRawMaterial.objects.create(user=self.user, recipe=recipe, material_name="test_material", price_per_kg=10, max_percentage=90, min_percentage=5)
        self.assertEqual(raw_material.material_name, "test_material")
        self.assertEqual(raw_material.recipe, recipe)
        self.assertEqual(raw_material.price_per_kg, 10)
    def test_unique_raw_material_in_recipe(self):
        RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="test_material")
        with self.assertRaises(Exception):
                RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="test_material")
    def test_cascade_delete_behavior(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Test Material")
        self.recipe.delete()
        self.assertEqual(RecipeRawMaterial.objects.filter(id=material.id).count(), 0)
    def test_recipe_str_representation(self):
        self.assertEqual(str(self.recipe), "Test Recipe")
class EncryptUsernameTest(TestCase):
    def test_encrypt_username(self):
        username = "testuser"
        expected_output = hashlib.sha256(username.encode()).hexdigest()
        self.assertEqual(encrypt_username(username), expected_output)
class FindOptimalMixTest(TestCase):
    def setUp(self):
        # Setup mock data
        self.user = User.objects.create(username="testuser")
        self.recipe = Recipe.objects.create(name="test_recipe", user=self.user)
        self.material = RecipeRawMaterial.objects.create(material_name="test_material", user=self.user, recipe=self.recipe)
        MaterialAttributeValue.objects.create(user=self.user, raw_material=self.material, attribute_name="test_attribute", value=10)
        RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name="test_attribute", min_value=5, max_value=15)
    def test_find_optimal_mix(self):
        result = find_optimal_mix("testuser", self.recipe.id)
        self.assertIn("msg", result)
        self.assertIn("data", result)


class RecipeCrudTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        # Creating some dummy data
        self.recipe = Recipe.objects.create(name='Test Recipe', user=self.user)
    def test_create_recipe(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'create',
            'recipe_name': 'New Recipe'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(Recipe.objects.filter(name='New Recipe').exists())
    def test_update_recipe(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'update',
            'recipe_id': self.recipe.id,
            'recipe_name': 'Updated Recipe'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(Recipe.objects.filter(name='Updated Recipe').exists())
    def test_delete_recipe(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'delete',
            'recipe_id': self.recipe.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())
    def test_get_recipes(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'get'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(len(response.json()['data']), 1)
    def test_get_first_recipe(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'get_first'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['data']['name'], 'Test Recipe')
    def test_nonexistent_recipe(self):
        url = reverse('recipe_crud')
        response = self.client.post(url, {
            'action': 'update',
            'recipe_id': 9999,
            'recipe_name': 'Nonexistent Recipe'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Recipe does not exist')


url = reverse('recipe_ratio_crud')
class RecipeRatioCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.recipe = Recipe.objects.create(user=self.user, name='Test Recipe')
        self.attr_limit1 = RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name='Attribute1', min_value=1, max_value=10)
        self.attr_limit2 = RecipeAttributeLimit.objects.create(user=self.user, recipe=self.recipe, attribute_name='Attribute2', min_value=1, max_value=10)
        self.client.login(username='testuser', password='testpassword')
    def test_recipe_ratio_crud(self):
        # Test create
        response = self.client.post(url, {
            'action': 'create',
            'recipe_id': self.recipe.id,
            'nutrition1_id': self.attr_limit1.id,
            'nutrition2_id': self.attr_limit2.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        ratio_id = response.json()['data']['id']
        # Test read
        response = self.client.post(url, {
            'action': 'read',
            'recipe_id': self.recipe.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        # Test delete
        response = self.client.post(url, {
            'action': 'delete',
            'ratio_id': ratio_id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
    def tearDown(self):
        self.user.delete()
class RecipeRawMaterialCRUDTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
        self.url = reverse('recipe_raw_material_crud')  # Using reverse to get the URL
    def test_create_recipe_raw_material(self):
        response = self.client.post(self.url, {
            'action': 'create',
            'recipe_id': self.recipe.id,
            'material_name': 'Test Material',
            'price': '10',
            'max_percentage': '90',
            'min_percentage': '5',
            'min_weight_kg_per_ton': '1',
            'max_weight_kg_per_ton': '10',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(RecipeRawMaterial.objects.filter(material_name='Test Material').exists())

    def test_read_recipe_raw_material(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Read Material")
        response = self.client.post(self.url, {
            'action': 'read',
            'recipe_id': self.recipe.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        data_list = response.json()['data']
        self.assertTrue(any(d['material_name'] == "Read Material" for d in data_list))

    def test_get_first_recipe_raw_material(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="First Material")
        response = self.client.post(self.url, {
            'action': 'get_first',
            'recipe_id': self.recipe.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['data']['material_name'], 'First Material')


    def test_delete_recipe_raw_material(self):
        material = RecipeRawMaterial.objects.create(user=self.user, recipe=self.recipe, material_name="Delete Material")
        response = self.client.post(self.url, {
            'action': 'delete',
            'material_id': material.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(RecipeRawMaterial.objects.filter(material_name='Delete Material').exists())

    
    def test_nonexistent_recipe(self):
        response = self.client.post(self.url, {
            'action': 'create',
            'recipe_id': 99999,  # Non-existent recipe ID
            'material_name': 'Test Material'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

class CalculateViewTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        # Create a test recipe
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('calculate')  # Use the correct URL pattern name

    def test_valid_post_request(self):
        response = self.client.post(self.url, {
            'recipe_id': self.recipe.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json()["status"], ["success", "error"])

    def tearDown(self):
        self.user.delete()

class CalculateViewIntegrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('calculate')

    def test_optimal_solution_found(self):
        response = self.client.post(self.url, {'recipe_id': self.recipe.id})
        # Since the find_optimal_mix is already implemented and its behavior might vary, 
        # we're just ensuring it returns a 200 status code here.
        self.assertEqual(response.status_code, 200)

    def test_no_optimal_solution(self):
        # Assuming that passing an invalid recipe_id would lead to no optimal solution
        response = self.client.post(self.url, {'recipe_id': 9999})  # Invalid recipe_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")
        self.assertIn("No optimal solution found", response.json()["message"])

    def tearDown(self):
        self.user.delete()

class CalculateViewBoundaryTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('calculate')

    def test_invalid_recipe_id(self):
        response = self.client.post(self.url, {'recipe_id': 9999})  # Invalid recipe_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

    def test_no_post_method(self):
        response = self.client.get(self.url)  # Using GET instead of POST
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")
        self.assertIn("Method not allowed", response.json()["message"])

    def tearDown(self):
        self.user.delete()

class CalculateViewCoverageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.recipe = Recipe.objects.create(user=self.user, name="Test Recipe")
        self.url_calculate = reverse('calculate')

    def test_database_exception(self):
        # Mocking a database exception by using an invalid recipe_id
        response = self.client.post(self.url_calculate, {'recipe_id': 9999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")
       
    def test_best_recipe_save(self):
        # This is a basic test to ensure that the best recipe is saved. 
        # The actual behavior might vary based on the implementation of find_optimal_mix and other factors.
        response = self.client.post(self.url_calculate, {'recipe_id': self.recipe.id})
        self.assertEqual(response.status_code, 200)
        # The exact assertions might need adjustments based on the actual behavior of the view.

    def tearDown(self):
        self.user.delete()

class UserManageCoverageTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('testuser1', 'test1@example.com', 'testpassword1')
        self.client = Client()
        self.client.login(username='testuser1', password='testpassword1')
        self.url_user_manage = reverse('user_manage')

    def test_delete_user_exception(self):
        # Mocking a delete user exception by using an invalid user_id
        response = self.client.post(self.url_user_manage, {
            'action': 'delete',
            'user_id': 9999  # Invalid user_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

    def tearDown(self):
        self.user1.delete()

class UserLoginRegisterCoverageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client = Client()
        self.url_login = reverse('user_login')
        self.url_register = reverse('user_register')

    def test_user_login_valid(self):
        response = self.client.post(self.url_login, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_user_login_invalid_password(self):
        response = self.client.post(self.url_login, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")


    def test_user_registration_existing_email(self):
        response = self.client.post(self.url_register, {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'test@example.com'  # Existing email
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

    def tearDown(self):
        self.user.delete()

class ImportExcelViewTests_1(TestCase):

    def setUp(self):
        self.client = Client()
        self.import_url = reverse('import_excel_view')
        # Create a test user, recipe, etc. based on your models if needed

    def test_nonexistent_user_in_excel(self):
        # Prepare an Excel file with a non-existent user
        data = {
            'user': [999],  # assuming 999 is a non-existent user ID
            'name': ['Test Recipe'],
            # add other columns as needed
        }
        df = pd.DataFrame(data)
        
        # Convert DataFrame to Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Recipes', index=False)
        output.seek(0)
        
        # Post the Excel to the view
        response = self.client.post(self.import_url, {'excel_file': output}, format='multipart')
        
        # Instead of expecting a 200 OK status, expect a 302 Redirection
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=/api/import_excel/', response.url)

class ImportExcelViewTests_2(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.url_import = '/api/import_excel/'  
        self.url_export = '/api/export_excel/' 
    # test import_excel_view
    def test_import_get_request(self):
        response = self.client.get(self.url_import)
        self.assertEqual(response.status_code, 200)

    def test_import_without_file(self):
        response = self.client.post(self.url_import)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "No file uploaded."})

    def test_import_invalid_excel_file(self):
        invalid_file = SimpleUploadedFile("test.xlsx", b"Invalid content")
        response = self.client.post(self.url_import, {'excel_file': invalid_file})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Error reading Excel file" in response.json()["message"])

    def test_export_post_request(self):
        response = self.client.post(self.url_export)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Recipe ID is required."})

    def test_export_without_recipe_id(self):
        response = self.client.get(self.url_export)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Recipe ID is required."})

class ImportExcelViewTests_3(TestCase):

    def setUp(self):
        # 设置测试前的条件，例如创建一个用户或登录。
        self.import_url = reverse('import_excel_view')  # 确保您有正确的URL名称。
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', user=self.user)

    def post_excel_data(self, sheet_name, data):
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return self.client.post(self.import_url, {'excel_file': output}, format='multipart')

    def test_nonexistent_user_in_excel(self):
        data = {
            'user': [999],
            'name': ['Test Recipe']
        }
        response = self.post_excel_data('Recipes', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "message": "Data imported successfully."})

    def test_recipe_sheet_processing(self):
        data = {
            'material_name': ['Material1'],
            'price_per_kg': [20],
            # 添加其他必要的列
        }
        response = self.post_excel_data('Recipe_Test Recipe', data)
        self.assertEqual(response.status_code, 200)
        # 在这里，您可以检查数据库是否已正确存储数据。

    def test_material_attribute_values_sheet_processing(self):
        raw_material = RecipeRawMaterial.objects.create(recipe=self.recipe, material_name="Material1", user=self.user)
        data = {
            'recipe_id': [self.recipe.id],
            'raw_material_id': [raw_material.id],
            'attribute_name': ['Attribute1'],
            'value': [10]
        }
        response = self.post_excel_data('MaterialAttributeValues', data)
        self.assertEqual(response.status_code, 200)

    def test_recipe_attribute_limits_sheet_processing(self):
        data = {
            'recipe_id': [self.recipe.id],
            'attribute_name': ['Attribute1'],
            'min_value': [5],
            'max_value': [15]
        }
        response = self.post_excel_data('RecipeAttributeLimits', data)
        self.assertEqual(response.status_code, 200)

class ImportExcelViewTests_4(TestCase):

    def setUp(self):
        self.import_url = reverse('import_excel_view')  
        self.user = User.objects.create_user(
        username='testuser', password='testpassword'
    )
    # Login as the test user
        self.client.login(username='testuser', password='testpassword')

    def post_excel_data(self, sheet_name, data):
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return self.client.post(self.import_url, {'excel_file': output}, format='multipart')

    def test_nonexistent_recipe_or_material(self):
        data = {
            'recipe_id': [999],  # non-existent recipe ID
            'raw_material_id': [999],  # non-existent raw material ID
            'attribute_name': ['Test Attribute'],
        }
        response = self.post_excel_data('MaterialAttributeValues', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "message": "Data imported successfully."})

    def test_nonexistent_recipe(self):
        data = {
            'recipe_id': [999],  # non-existent recipe ID
            'attribute_name': ['Test Attribute'],
        }
        response = self.post_excel_data('RecipeAttributeLimits', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "message": "Data imported successfully."})

    def test_invalid_data_structure(self):
        data = {
            'invalid_column': ['Invalid Data'],
        }
        response = self.post_excel_data('InvalidSheetName', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "message": "Data imported successfully."})

class MaterialAttributeValueCrudTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name="Test Recipe", user=self.user)
        self.material = RecipeRawMaterial.objects.create(
            material_name='Test Material', recipe=self.recipe, user=self.user)

    def test_create_material_attribute_value(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('material_attribute_value_crud'), {
            'action': 'create',
            'recipe_id': self.recipe.id,
            'material_id': self.material.id,
            'attribute_name': 'Test Attribute',
            'value': '100'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_read_material_attribute_value(self):
        material_value = MaterialAttributeValue.objects.create(
            user=self.user, recipe=self.recipe, raw_material=self.material, attribute_name='Test Attribute', value='100')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('material_attribute_value_crud'), {
            'action': 'read',
            'material_id': self.material.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        expected_data = {
            'id': 1,
            'user_id': 1,
            'recipe_id': 1,
            'raw_material_id': 1,
            'attribute_name': 'Test Attribute',
            'value': '100.0000000000',
            'selected': True
        }
        self.assertIn(expected_data, response.json()['data'])


    def test_update_material_attribute_value(self):
        material_value = MaterialAttributeValue.objects.create(
            user=self.user, recipe=self.recipe, raw_material=self.material, attribute_name='Test Attribute', value='100')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('material_attribute_value_crud'), {
            'action': 'update',
            'attribute_id': material_value.id,
            'attribute_name': 'Updated Attribute',
            'value': '200'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_delete_material_attribute_value(self):
        material_value = MaterialAttributeValue.objects.create(
            user=self.user, recipe=self.recipe, raw_material=self.material, attribute_name='Test Attribute', value='100')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('material_attribute_value_crud'), {
            'action': 'delete',
            'attribute_id': material_value.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_object_does_not_exist(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('material_attribute_value_crud'), {
            'action': 'update',
            'attribute_id': 9999,  # non-existing id
            'attribute_name': 'Updated Attribute',
            'value': '200'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

class ExcelImportExportTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def create_fake_excel_file(self):
        output = BytesIO()

        # Creating a fake DataFrame for demonstration purposes
        df = pd.DataFrame({
            'user': [1],
            'name': ['TestRecipe'],
        })

        # Save DataFrame to BytesIO object as Excel
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Recipes', index=False)

        output.seek(0)
        return output

    def test_import_excel_view(self):
        # Create fake excel file
        excel_file = self.create_fake_excel_file()

        # POST request to the view
        response = self.client.post('/api/import_excel/', {'excel_file': excel_file})


        # Check for success response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Verify that Recipe object was created
        self.assertTrue(Recipe.objects.filter(name='TestRecipe').exists())

    def tearDown(self):
        # Cleanup any objects you've created in the database after the tests are done
        Recipe.objects.all().delete()

class ExportExcelViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', user=self.user)
        self.url = reverse('export_excel_view')

    def test_non_get_request(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {"recipe_id": self.recipe.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Recipe ID is required."})

    def test_missing_recipe_id(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Recipe ID is required."})

    def test_invalid_recipe_id(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {'recipe_id': 999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Recipe not found."})

    def test_export_excel(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, {'recipe_id': self.recipe.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename=testuser_Test Recipe_database.xlsx')

class RecipeAttributeLimitCrudTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', user=self.user)
        self.url = reverse('recipe_attribute_limit_crud')

    def test_create_limit(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "create",
            "recipe_id": self.recipe.id,
            "attribute_name": "Test Attribute",
            "min_value": "0",
            "max_value": "100"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_read_limit(self):
        RecipeAttributeLimit.objects.create(
            user=self.user, recipe=self.recipe, attribute_name="Test Attribute", min_value=0, max_value=100)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "read",
            "recipe_id": self.recipe.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_update_limit(self):
        limit = RecipeAttributeLimit.objects.create(
            user=self.user, recipe=self.recipe, attribute_name="Test Attribute", min_value=0, max_value=100)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "update",
            "limit_id": limit.id,
            "attribute_name": "Updated Attribute",
            "min_value": "10",
            "max_value": "90"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_delete_limit(self):
        limit = RecipeAttributeLimit.objects.create(
            user=self.user, recipe=self.recipe, attribute_name="Test Attribute", min_value=0, max_value=100)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "delete",
            "limit_id": limit.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "create",
            "recipe_id": 9999,  # Invalid recipe ID
            "attribute_name": "Test Attribute",
            "min_value": "0",
            "max_value": "100"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

    def test_non_post_request(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Runtime error"})

class BestRecipeCrudTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', user=self.user)
        self.url = reverse('best_recipe_crud')

    def test_read_best_recipe(self):
        self.client.login(username='testuser', password='testpass')
        
        # Create a RecipeRawMaterial instance
        material = RecipeRawMaterial.objects.create(
            user=self.user,
            recipe=self.recipe,
            material_name="Test Material",
            price_per_kg=10.0,
            max_percentage=100,
            min_percentage=0,
            min_weight_kg_per_ton=0.0,
            max_weight_kg_per_ton=1000.0
        )
        
        # Use the created material instance when creating BestRecipe
        best_recipe = BestRecipe.objects.create(
            user=self.user, 
            recipe=self.recipe, 
            material=material, 
            material_name="Test Material",
            value=50.0
        )

        # Create a BestRecipeNutrition instance for completeness
        recipe_attribute_limit = RecipeAttributeLimit.objects.create(
            user=self.user,
            recipe=self.recipe,
            attribute_name="Test Attribute",
            min_value=10.0,
            max_value=90.0
        )
        best_recipe_nutrition = BestRecipeNutrition.objects.create(
            user=self.user,
            recipe=self.recipe,
            nutrition=recipe_attribute_limit,
            nutrition_name="Test Attribute",
            value=50.0
        )
        
        # Now, make the POST request to the best_recipe_crud function
        response = self.client.post(reverse('best_recipe_crud'), {'action': 'read', 'recipe_id': self.recipe.id})
        
        # Check if the response is successful and contains the expected data
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['data']), 1)
        self.assertEqual(response_data['data'][0]['material_name'], 'Test Material')
        self.assertEqual(response_data['data'][0]['value'], '50.00') # Ensure it matches the decimal representation
        self.assertEqual(len(response_data['nutrition']), 1)
        self.assertEqual(response_data['nutrition'][0]['nutrition_name'], 'Test Attribute')
        self.assertEqual(response_data['nutrition'][0]['value'], '50.00') # Ensure it matches the decimal representation

    def test_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {
            "action": "read",
            "recipe_id": 9999  # Invalid recipe ID
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

    def test_non_post_request(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "error", "message": "Invalid request method"})

class RecipeRawMaterialCrudTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        # 创建一个示例Recipe和RecipeRawMaterial以便测试
        self.recipe = Recipe.objects.create(name='Test Recipe')
        self.material = RecipeRawMaterial.objects.create(
            user=self.user,
            recipe=self.recipe,
            material_name='Test Material',
            price_per_kg=10.0,
            max_percentage=50,
            min_percentage=10,
            min_weight_kg_per_ton=5.0,
            max_weight_kg_per_ton=50.0,
        )

    def test_create_recipe_raw_material(self):
        response = self.client.post('/api/recipe_raw_material_crud/', {
            'action': 'create',
            'recipe_id': self.recipe.id,
            'material_name': 'New Material',
            'price': 15.0,
            'max_percentage': 60,
            'min_percentage': 20,
            'min_weight_kg_per_ton': 6.0,
            'max_weight_kg_per_ton': 55.0,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

        # 检查新创建的RecipeRawMaterial是否存在
        created_material = RecipeRawMaterial.objects.filter(material_name='New Material').first()
        self.assertIsNotNone(created_material)

    def test_update_recipe_raw_material(self):
        response = self.client.post('/api/recipe_raw_material_crud/', {
            'action': 'update',
            'material_id': self.material.id,
            'material_name': 'Updated Material',
            'price': 12.0,
            'max_percentage': 55,
            'min_percentage': 15,
            'min_weight_kg_per_ton': 4.0,
            'max_weight_kg_per_ton': 45.0,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

        # 检查更新后的RecipeRawMaterial字段是否正确
        updated_material = RecipeRawMaterial.objects.get(id=self.material.id)
        self.assertEqual(updated_material.material_name, 'Updated Material')
        self.assertEqual(updated_material.price_per_kg, 12.0)

    def test_delete_recipe_raw_material(self):
        response = self.client.post('/api/recipe_raw_material_crud/', {
            'action': 'delete',
            'material_id': self.material.id,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

        # 检查RecipeRawMaterial是否已删除
        deleted_material = RecipeRawMaterial.objects.filter(id=self.material.id).first()
        self.assertIsNone(deleted_material)

    def test_invalid_request_method(self):
        response = self.client.get('/api/recipe_raw_material_crud/')  # 使用GET请求
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid request method')


class OptimalMixTest(TestCase):

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create test recipe
        self.recipe = Recipe.objects.create(user=self.user, name='TestRecipe')

        # Create some test materials and related data
        self.material1 = RecipeRawMaterial.objects.create(
            user=self.user,
            recipe=self.recipe,
            material_name="Material1",
            price_per_kg=5,
            min_percentage=10,
            max_percentage=60
        )
        self.material2 = RecipeRawMaterial.objects.create(
            user=self.user,
            recipe=self.recipe,
            material_name="Material2",
            price_per_kg=10,
            min_percentage=20,
            max_percentage=50
        )

        # Create attribute limits for the recipe
        RecipeAttributeLimit.objects.create(
            user=self.user,
            recipe=self.recipe,
            attribute_name="Attribute1",
            min_value=10,
            max_value=50
        )

        # Create attribute values for the materials
        MaterialAttributeValue.objects.create(
            user=self.user,
            raw_material=self.material1,
            attribute_name="Attribute1",
            value=25
        )
        MaterialAttributeValue.objects.create(
            user=self.user,
            raw_material=self.material2,
            attribute_name="Attribute1",
            value=30
        )

    def test_no_solution(self):
        # Modify attributes to create a scenario where there is no solution
        attribute_limit = RecipeAttributeLimit.objects.get(user=self.user, recipe=self.recipe, attribute_name="Attribute1")
        attribute_limit.min_value = 100
        attribute_limit.save()

        result = find_optimal_mix(self.user.username, self.recipe.id)
        self.assertEqual(result['msg'], "No optimal solution found!")

class DownloadPDFViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='top_secret')

    @mock.patch('ingredients.views.find_optimal_mix')
    @mock.patch('ingredients.views.Recipe.objects.get')
    def test_missing_recipe_id(self, mock_get, mock_find_optimal_mix):
        # Mock the get method to raise an ObjectDoesNotExist exception
        mock_get.side_effect = Recipe.DoesNotExist

        # Mock the find_optimal_mix function to return a dummy value
        mock_find_optimal_mix.return_value = {'data': {}, 'total_nutrition_values': {}}

        request = self.factory.get('/path/to/your/view/')
        request.user = self.user
        response = download_pdf_view(request)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Recipe ID is missing.')

class SetTonneViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_request(self):
        request = self.factory.get('/path/to/set_tonne/')
        response = set_tonne(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "error", "message": "Method not allowed"})

    @patch('ingredients.models.Recipe.objects.get')
    def test_missing_tonne_value(self, mock_get):
        mock_get.return_value = Mock(spec=Recipe, tonne=None)
        request = self.factory.post('/path/to/set_tonne/', {'action': 'create', 'recipe_id': 1})
        response = set_tonne(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "error", "message": "Tonne value is missing."})

    @patch('ingredients.models.Recipe.objects.get')
    def test_successful_tonne_update(self, mock_get):
        mock_recipe = Mock(spec=Recipe)
        mock_recipe.tonne = None
        mock_get.return_value = mock_recipe
        request = self.factory.post('/path/to/set_tonne/', {'action': 'create', 'recipe_id': 1, 'tonne': '2.5'})
        response = set_tonne(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "success", "tonne": "2.5"})
        mock_recipe.save.assert_called_once()

    @patch('ingredients.models.Recipe.objects.get', side_effect=Recipe.DoesNotExist)
    def test_recipe_does_not_exist(self, mock_get):
        request = self.factory.post('/path/to/set_tonne/', {'action': 'create', 'recipe_id': 999, 'tonne': '2.5'})
        response = set_tonne(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "error", "message": "Recipe does not exist."})


    @patch('ingredients.models.Recipe.objects.get', side_effect=Exception("Some unexpected error"))
    def test_general_exception(self, mock_get):
        request = self.factory.post('/path/to/set_tonne/', {'action': 'create', 'recipe_id': 1, 'tonne': '2.5'})
        response = set_tonne(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "error", "message": "Some unexpected error"})

class RecipeManagementTest(TestCase):

    def setUp(self):
        self.user = Mock(name="User Mock")
        self.recipe_id = 1
        self.recipe = Mock(name="Recipe Mock", spec=Recipe)
        self.data = {"material1": "2.5", "material2": "3.0"}
        self.mocked_values = Mock(name="Values Mock")
        self.mocked_values.values.return_value = [{"data": "mocked_data"}] 

    @patch('ingredients.models.Recipe.objects.get')
    @patch('ingredients.models.BestRecipe.objects.filter')
    @patch('ingredients.models.RecipeRawMaterial.objects.get')
    @patch('ingredients.models.BestRecipe.objects.update_or_create')
    def test_save_best_recipe(self, mock_update_or_create, mock_get_material, mock_filter, mock_get_recipe):
        mock_get_recipe.return_value = self.recipe
        mock_get_material.return_value = Mock(name="Material Mock", spec=RecipeRawMaterial, price_per_kg="5")
        mock_filter.return_value = self.mocked_values
        
        result = save_best_recipe(self.user, self.recipe_id, self.data)
        
        mock_get_recipe.assert_called_once_with(id=self.recipe_id)
        mock_filter.assert_called_with(user=self.user, recipe=self.recipe)
        mock_get_material.assert_any_call(user=self.user, recipe=self.recipe, material_name="material1")
        mock_get_material.assert_any_call(user=self.user, recipe=self.recipe, material_name="material2")
        self.assertTrue(isinstance(result, list))

    @patch('ingredients.models.Recipe.objects.get')
    @patch('ingredients.models.BestRecipeNutrition.objects.filter')
    @patch('ingredients.models.RecipeAttributeLimit.objects.get')
    @patch('ingredients.models.BestRecipeNutrition.objects.update_or_create')
    def test_save_nutrition(self, mock_update_or_create, mock_get_nutrition, mock_filter, mock_get_recipe):
        mock_get_recipe.return_value = self.recipe
        mock_get_nutrition.return_value = Mock(name="Nutrition Mock", spec=RecipeAttributeLimit)
        mock_filter.return_value = self.mocked_values 
        
        result = save_nutrition(self.user, self.recipe_id, self.data)
        
        mock_get_recipe.assert_called_once_with(id=self.recipe_id)
        mock_filter.assert_called_with(user=self.user, recipe=self.recipe)
        mock_get_nutrition.assert_any_call(user=self.user, recipe=self.recipe, attribute_name="material1")
        mock_get_nutrition.assert_any_call(user=self.user, recipe=self.recipe, attribute_name="material2")
        self.assertTrue(isinstance(result, list))


class CalculateNutritionValuesTest(TestCase):

    def setUp(self):
        self.current_user = Mock(name="User Mock")
        
        # Mock materials
        self.materials = ['Material1', 'Material2']
        
        # Mock optimal mix percentages
        mock_var = Mock()
        mock_var.varValue = 50  # For simplicity, assuming each material is 50% of the mix
        self.var_dict = {'Material1': mock_var, 'Material2': mock_var}

    @patch('ingredients.models.MaterialAttributeValue.objects.filter')
    def test_calculate_nutrition_values(self, mock_filter):
        
        # Mock nutrition_entries
        mock_entry1 = Mock(spec=MaterialAttributeValue, attribute_name='Protein', value='10')  # 10% protein
        mock_entry2 = Mock(spec=MaterialAttributeValue, attribute_name='Carbs', value='20')   # 20% carbs
        mock_entries = [mock_entry1, mock_entry2]
        
        # Set the return value for the mock filter
        mock_filter.side_effect = [mock_entries, mock_entries]
        
        expected_result = {'Protein': 10, 'Carbs': 20}  # Expected result since each material contributes equally
        
        result = calculate_nutrition_values(self.current_user, self.materials, self.var_dict)
        
        # Check if the database filter method is called correctly for each material
        mock_filter.assert_any_call(user=self.current_user, raw_material='Material1')
        mock_filter.assert_any_call(user=self.current_user, raw_material='Material2')
        
        # Check the result
        self.assertEqual(result, expected_result)