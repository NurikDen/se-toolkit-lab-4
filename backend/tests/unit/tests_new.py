# test_interactions_edge_cases.py

import pytest
from fastapi.testclient import TestClient
from main import app  # предположительный импорт
from datetime import datetime, timedelta

client = TestClient(app)

def test_create_interaction_nonexistent_learner():
    """Тест: попытка создать взаимодействие с несуществующим learner_id"""
    # Подготовка
    interaction_data = {
        "learner_id": 99999,  # несуществующий ID
        "item_id": 1,
        "kind": "view"
    }
    
    # Действие
    response = client.post("/interactions", json=interaction_data)
    
    # Проверка
    assert response.status_code == 404
    assert "learner_id" in response.text.lower()

def test_create_interaction_nonexistent_item():
    """Тест: попытка создать взаимодействие с несуществующим item_id"""
    interaction_data = {
        "learner_id": 1,
        "item_id": 99999,  # несуществующий ID
        "kind": "attempt"
    }
    
    response = client.post("/interactions", json=interaction_data)
    
    assert response.status_code == 404
    assert "item_id" in response.text.lower()

def test_interaction_invalid_kind_value():
    """Тест: граничное значение - недопустимый тип взаимодействия"""
    interaction_data = {
        "learner_id": 1,
        "item_id": 1,
        "kind": "invalid_kind_123"  # не из списка допустимых
    }
    
    response = client.post("/interactions", json=interaction_data)
    
    assert response.status_code == 422  # Validation error
    assert "kind" in response.text.lower()

def test_interaction_future_timestamp():
    """Тест: граничное значение - timestamp в будущем"""
    future_time = (datetime.now() + timedelta(days=365)).isoformat()
    
    interaction_data = {
        "learner_id": 1,
        "item_id": 1,
        "kind": "view",
        "created_at": future_time
    }
    
    response = client.post("/interactions", json=interaction_data)
    
    # Сервер должен либо принять (если нет валидации), либо отклонить
    # Проверяем, что ответ вообще пришёл
    assert response.status_code in [200, 201, 400, 422]

def test_create_learner_max_length_name():
    """Тест: граничное значение - максимальная длина имени"""
    long_name = "A" * 255  # граничное значение
    
    learner_data = {
        "name": long_name,
        "email": f"{long_name[:50]}@example.com"  # обрезаем для email
    }
    
    response = client.post("/learners", json=learner_data)
    
    # Должно либо создать (201), либо вернуть ошибку валидации (422)
    assert response.status_code in [201, 422]
    if response.status_code == 201:
        data = response.json()
        assert data["name"] == long_name