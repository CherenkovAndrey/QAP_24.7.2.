from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password, very_long_name, very_long_age
import os
pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key."""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Вилли', animal_type='Корги', age='3',
                                     pet_photo='images/velsh-korgi-pembrok.jpg'):
    """ Проверяем что можно добавить питомца с корректными данными."""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age


def test_successful_update_self_pet_info(name='Билли', animal_type='Собака', age='4'):
    """ Проверяем возможность обновления информации о питомце."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Еслди список не пустой, то пробуем обновить его имя, итип  возраст.
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        # Проверяем что статус ответа = 200 и данные питомца соответствует заданным.
        assert status == 200
        assert result['name'] == name
        assert result['animal_type'] == animal_type
        assert result['age'] == age
    else:
        raise Exception("У меня нет питомцев")


def test_successful_delete_self_pet():
    """ Проверяем возможность удаления питомца."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Добавляем нового если список пуст.
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Test-pet", "test", "123")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in my_pets.values()




def test_create_pet_simple(name='Вася', animal_type='Кот', age='3'):
    """ Проверяем возможность добавления питомца без фото."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age


def test_adding_photo_to_pet(pet_photo='images/Cat123.jpg'):
    """ Проверяем возможность добавления фото к уже существующему питомцу."""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Добавляем нового если список пуст.
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Test-pet", "test", "123")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    status, result = pf.pets_set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
    assert status == 200


def test_get_api_key_for_invalid_emai_and_password(email=invalid_email, password=invalid_password):
    """Проверяем что запрос не даёт api ключ при невалидных email и пароле."""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """Проверяем что запрос не даёт api ключ при невалидом пароле."""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_api_key_for_invalid_emai(email=invalid_email, password=valid_password):
    """Проверяем что запрос не даёт api ключ при невалидном email."""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_create_pet_simple_with_invalid_auth_key(name='Вася', animal_type='Кот', age='3'):
    """ Проверка невозможности создания питомца при неверном ключе авторизации."""
    invalid_auth_key = {"key": "a27aadb613116dfd656a96f42aed887a4fc371acb748f7637634f69"}
    status, result = pf.create_pet_simple(invalid_auth_key, name, animal_type, age)
    assert status == 403


def test_delete_self_pet_with_invalid_auth_key():
    """Проверка невозможности удаления питомца при неверном ключе авторизации."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    invalid_auth_key = {"key": "abcdefjhijklmo1234567889"}
    # Добавляем нового питомца если список пуст.
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Test-pet", "test", "123")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(invalid_auth_key, pet_id)
    assert status == 403


def test_update_pet_info_with_invalid_auth_key(name='Вася', animal_type='Кот', age='3'):
    """Проверка невозможности обновления информации о питомце при неверном ключе авторизации"""
    invalid_auth_key = {"key": "abcdefjhijklmo1234567889"}
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Добавляем нового питомца если список пуст.
    if len(my_pets['pets']) == 0:
        pf.create_pet_simple(auth_key, "Test-pet", "test", "123")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    status, result = pf.update_pet_info(invalid_auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
    assert status == 403


def test_create_pet_with_very_long_name(name= very_long_name, animal_type='Животное', age= very_long_age):
    """ Проверяем возможность добавления питомца с очень болшими значениями."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age


def test_create_pet_with_empty_values(name="", animal_type="", age=""):
    """ Проверяем возможность добавления питомца с пустыми значениями."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age
