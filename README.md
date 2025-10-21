# String Analyzer API (Stage 1 - HNG)

A RESTful API built with **FastAPI** that analyzes strings and stores their computed properties.

## Features
- Computes and stores:
  - length
  - palindrome check
  - unique character count
  - word count
  - SHA-256 hash
  - character frequency map
- Retrieve and filter stored strings
- Delete strings
- Natural language query filtering

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nodebugger/string_analyzer.git
   cd string_analyzer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv string_venv
   source string_venv/Scripts/activate  # On Windows
   # Or
   source string_venv/bin/activate      # On Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   The database is initialized automatically on server startup.

5. **Run the API server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### 1. Create/Analyze String

**POST /strings**

- Request Body:
  ```json
  {
    "value": "string to analyze"
  }
  ```
- Success Response:
  ```json
  {
    "id": "<sha256_hash>",
    "value": "string to analyze",
    "properties": {
      "length": 17,
      "is_palindrome": false,
      "unique_characters": 12,
      "word_count": 3,
      "sha256_hash": "<sha256_hash>",
      "character_frequency_map": { "s": 2, "t": 3, ... }
    },
    "created_at": "2025-08-27T10:00:00Z"
  }
  ```

### 2. Get Specific String

**GET /strings/{string_value}**

- Success Response:
  ```json
  {
    "id": "<sha256_hash>",
    "value": "requested string",
    "properties": { ... },
    "created_at": "2025-08-27T10:00:00Z"
  }
  ```

### 3. Get All Strings with Filtering

**GET /strings**

- Query Parameters:
  - `is_palindrome`: boolean
  - `min_length`: integer
  - `max_length`: integer
  - `word_count`: integer
  - `contains_character`: string

- Example:
  ```
  GET /strings?is_palindrome=true&min_length=5&contains_character=a
  ```

- Success Response:
  ```json
  {
    "data": [ ... ],
    "count": 3,
    "filters_applied": {
      "is_palindrome": true,
      "min_length": 5,
      "contains_character": "a"
    }
  }
  ```

### 4. Natural Language Filtering

**GET /strings/filter-by-natural-language?query={query}**

- Example:
  ```
  GET /strings/filter-by-natural-language?query=all single word palindromic strings
  ```
- Success Response:
  ```json
  {
    "data": [ ... ],
    "count": 2,
    "interpreted_query": {
      "original": "all single word palindromic strings",
      "parsed_filters": {
        "word_count": 1,
        "is_palindrome": true
      }
    }
  }
  ```

### 5. Delete String

**DELETE /strings/{string_value}**

- Success Response:  
  Status code `204 No Content` (empty body)

## Error Handling

- `409 Conflict`: String already exists
- `400 Bad Request`: Invalid request or missing fields
- `404 Not Found`: String does not exist
- `422 Unprocessable Entity`: Invalid data type for "value"

## Example Usage (with curl)

```bash
# Create a string
curl -X POST "http://127.0.0.1:8000/strings" -H "Content-Type: application/json" -d '{"value": "racecar"}'

# Get all palindromic strings
curl "http://127.0.0.1:8000/strings?is_palindrome=true"

# Natural language filter
curl "http://127.0.0.1:8000/strings/filter-by-natural-language?query=all single word palindromic strings"

# Delete a string
curl -X DELETE "http://127.0.0.1:8000/strings/racecar"
```

## Running Tests

Run the provided test scripts after starting the server:
```bash
python test_endpoints.py
```
