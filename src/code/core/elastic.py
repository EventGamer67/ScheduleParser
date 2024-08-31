import os
from elasticsearch import Elasticsearch

elastic_username = 'elastic'
elastic_password = '12345678' 

# Подключение к Elasticsearch
elastic_client = Elasticsearch(
  "http://localhost:9200",
  basic_auth=(elastic_username, elastic_password)
)

def elastic_find_course_name(synonym):
    # Запрос на поиск с использованием inner_hits
    query = {
        "size": 1,  # Ограничиваем количество результатов до 1
        "query": {
            "nested": {
                "path": "courses",
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"courses.name": synonym}},
                            {"match": {"courses.syn": synonym}}
                        ]
                    }
                },
                "inner_hits": {  # Используем inner_hits для получения вложенного объекта
                    "size": 1,  # Получаем только один вложенный объект
                    "_source": ["courses.name", "courses.syn"]  # Только нужные поля
                }
            }
        }
    }
    # Выполнение поиска
    resp = elastic_client.search(index='courses', body=query)
    
    # Получение одного наилучшего вложенного результата
    if resp['hits']['hits']:
        # Доступ к inner_hits для получения наилучшего вложенного объекта
        inner_hits = resp['hits']['hits'][0].get('inner_hits', {})
        if inner_hits and 'courses' in inner_hits:
            best_nested_result = inner_hits['courses']['hits']['hits'][0]['_source']
            return best_nested_result['name']  # Вернуть только вложенный объект
    return None  # Если результатов нет


def elastic_init_dict():
    # Удаление индекса, если он существует
    if elastic_client.indices.exists(index='courses'):
        elastic_client.indices.delete(index='courses')

    # Создание индекса с правильным мэппингом
    elastic_client.indices.create(index='courses', body={
        "mappings": {
            "properties": {
                "courses": {
                    "type": "nested",  # Указание, что 'courses' - вложенный тип
                    "properties": {
                        "name": {"type": "text"},
                        "syn": {"type": "text"}
                    }
                }
            }
        }
    })

    # Добавление документа
    resp = elastic_client.index(
        index='courses',
        id="1",
        document={
            'courses': [
                {
                    "name": "Математика",
                    "syn": ['мат', 'матем']
                },
                {
                    "name": "Математическое моделирование",
                    "syn": ['мат мод']
                },
                {
                    "name": "Информатика",
                    "syn": ['инф', 'информатик']
                },
                {
                    "name": "История",
                    "syn": ['истор']
                }
            ]
        }
    )
    # Обновление индекса
    elastic_client.indices.refresh(index='courses')

# Инициализация индекса и добавление данных
elastic_init_dict()
print(elastic_find_course_name("инф"))
