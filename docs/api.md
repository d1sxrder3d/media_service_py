# Справочник API

Интерактивная документация API (Swagger) доступна по адресу: `http://localhost:8000/docs`

---

### 1. Запуск задачи на обработку изображений

**`POST /v1/process`**

Создает новую задачу на обработку одного или нескольких изображений.

**Параметры (`form-data`):**

- `path` (string, required): Логический путь для сохранения (например, `products`, `avatars`).
- `id` (string, required): Уникальный идентификатор сущности (например, UUID продукта).
- `resolution` (string, required): Целевое разрешение по ширине. Доступные значения: `320`, `480`, `720`, `1080`, `2k`, `original`.
- `images` (file, required): Один или несколько файлов изображений.

**Пример запроса (`curl`):**

```bash
curl -X POST \
  -F "path=products" \
  -F "id=123e4567-e89b-12d3-a456-426614174000" \
  -F "resolution=1080" \
  -F "images=@/path/to/your/image1.png" \
  -F "images=@/path/to/your/image2.jpg" \
  http://localhost:8000/v1/process
```

**Пример успешного ответа (200 OK):**

Сервер немедленно отвечает, подтверждая, что задача принята в очередь.

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "queued"
}
```

---

### 2. Получение статуса задачи

**`GET /v1/jobs/{job_id}`**

Возвращает информацию о статусе и результатах выполнения задачи.

**Пример запроса (`curl`):**

```bash
curl http://localhost:8000/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef
```

**Примеры ответов:**

*   **Задача в очереди или в процессе выполнения:**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "processing",
      "results": null,
      "error": null,
      "created_at": "2023-10-27T10:30:00.123Z",
      "updated_at": "2023-10-27T10:30:01.456Z"
    }
    ```

*   **Задача успешно выполнена:**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "done",
      "results": [
        "http://localhost:9000/images/products/123e4567-e89b-12d3-a456-426614174000/image1.webp",
        "http://localhost:9000/images/products/123e4567-e89b-12d3-a456-426614174000/image2.webp"
      ],
      "error": null
    }
    ```

*   **Задача выполнена с ошибками (частичный успех):**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "partial_success",
      "results": [
        "http://localhost:9000/images/products/123e4567-e89b-12d3-a456-426614174000/image1.webp"
      ],
      "error": "Unsupported image format, Another error message"
    }
    ```
