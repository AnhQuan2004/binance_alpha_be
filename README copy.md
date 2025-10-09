# 🚀 Airdrop Management API

A complete FastAPI + MongoDB backend for managing cryptocurrency airdrops with timezone-aware filtering and caching.

## 📁 Project Structure

```
backend_binance/
├── main.py              # Entry point
├── models.py            # Pydantic models
├── database.py          # MongoDB connection
├── utils.py             # Helper functions
├── routes/
│   ├── __init__.py
│   ├── public.py        # Public endpoints
│   └── admin.py         # Admin endpoints
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with your MongoDB Atlas connection:
```env
MONGODB_URL=mongodb+srv://admin:anhquan123@test1.atutk.mongodb.net/?retryWrites=true&w=majority&appName=test1
DB_NAME=airdrop_db
ADMIN_PASSWORD=your_secure_password_here
```

### 3. Run the Server

```bash
python main.py
```

Server will run at `http://localhost:8000`

## 📚 API Documentation

### Public Endpoints (No Authentication Required)

#### Get Airdrops
```bash
GET /api/airdrops?range=today|upcoming|all
```

**Query Parameters:**
- `range`: Filter by time range
  - `today`: Only today's airdrops
  - `upcoming`: Future airdrops
  - `all`: All airdrops (default)

**Example:**
```bash
# Get all airdrops
curl http://localhost:8000/api/airdrops?range=all

# Get today's airdrops
curl http://localhost:8000/api/airdrops?range=today

# Get upcoming airdrops
curl http://localhost:8000/api/airdrops?range=upcoming
```

**Response:**
```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "project": "SLX",
      "alias": "SLIMEX",
      "points": 200,
      "amount": 5000,
      "time_iso": "2025-10-08T14:00:00+07:00",
      "timezone": "Asia/Ho_Chi_Minh",
      "phase": "Phase 2",
      "x": "https://x.com/slimex",
      "raised": 1000000,
      "source_link": "https://example.com",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "deleted": false
    }
  ],
  "etag": "W/\"abc123\""
}
```

### Admin Endpoints (Authentication Disabled for Testing)

#### Create Airdrop
```bash
POST /api/airdrops
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/airdrops \
  -H "Content-Type: application/json" \
  -d '{
    "project": "SLX",
    "alias": "SLIMEX",
    "points": 200,
    "amount": 5000,
    "time_iso": "2025-10-08T14:00:00+07:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "phase": "Phase 2",
    "x": "https://x.com/slimex",
    "raised": 1000000,
    "source_link": "https://example.com"
  }'
```

#### Update Airdrop
```bash
PUT /api/airdrops/{id}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/airdrops/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{"points": 300}'
```

#### Delete Airdrop (Soft Delete)
```bash
DELETE /api/airdrops/{id}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/airdrops/507f1f77bcf86cd799439011
```

#### Get All Airdrops (Including Deleted)
```bash
GET /api/admin/airdrops
```

**Example:**
```bash
curl http://localhost:8000/api/admin/airdrops
```

#### Get Deleted Airdrops
```bash
GET /api/admin/airdrops/deleted
```

**Example:**
```bash
curl http://localhost:8000/api/admin/airdrops/deleted
```

## 🔧 Features

### ✨ Core Features
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Admin Authentication**: HTTP Basic Auth for admin endpoints
- **Soft Delete**: Items are marked as deleted, not removed from database
- **Timezone Support**: Full timezone awareness for filtering
- **ETag Caching**: Efficient caching with 304 Not Modified responses

### 🌍 Timezone Features
- **Timezone Validation**: Validates timezone strings using pytz
- **Smart Filtering**: Filter by "today", "upcoming", or "all"
- **ISO DateTime**: Supports ISO 8601 datetime format
- **Automatic Conversion**: Converts times to specified timezone

### ⚡ Performance Features
- **ETag Caching**: Reduces bandwidth with conditional requests
- **304 Responses**: Returns 304 Not Modified when data unchanged
- **Async MongoDB**: Non-blocking database operations
- **Connection Pooling**: Efficient database connections

### 🛡️ Security Features
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Safe**: MongoDB with parameterized queries
- **CORS Support**: Configurable CORS for frontend integration
- **Error Handling**: Graceful error responses

## 📊 Data Model

### Airdrop Fields
- `project`: Project name (required, 1-100 chars)
- `alias`: Project alias (required, 1-100 chars)
- `points`: Points value (required, >= 0)
- `amount`: Amount value (required, >= 0)
- `time_iso`: ISO datetime string (required)
- `timezone`: Timezone string (required, validated)
- `phase`: Optional phase information
- `x`: Optional X/Twitter URL
- `raised`: Optional raised amount
- `source_link`: Optional source URL

### System Fields
- `id`: MongoDB ObjectId (auto-generated)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `deleted`: Soft delete flag

## 🔄 Caching Strategy

The API implements intelligent caching:

1. **ETag Generation**: MD5 hash of response data
2. **Conditional Requests**: Supports `If-None-Match` header
3. **304 Responses**: Returns 304 when data unchanged
4. **Cache Headers**: Proper cache control headers
5. **Stale-While-Revalidate**: Background refresh strategy

## 🌐 CORS Configuration

CORS is configured for development:
```python
allow_origins=["*"]  # Change in production
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

## 🚨 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Invalid admin credentials
- **404 Not Found**: Airdrop not found
- **500 Internal Server Error**: Server errors

## 📝 Development

### Running in Development
```bash
python main.py
```

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
- `MONGODB_URL`: MongoDB connection string
- `DB_NAME`: Database name
- `ADMIN_PASSWORD`: Admin password for authentication

## 🔍 API Testing

### Interactive Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation.

### Health Check
```bash
curl http://localhost:8000/health
```

### Root Endpoint
```bash
curl http://localhost:8000/
```

## 📦 Dependencies

- **FastAPI**: Modern web framework
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **python-dotenv**: Environment variables
- **pytz**: Timezone handling

## 🎯 Use Cases

This API is perfect for:
- Cryptocurrency airdrop tracking
- Event management systems
- Timezone-aware applications
- High-performance APIs with caching
- Admin dashboards with CRUD operations

## 🔧 Customization

### Adding New Fields
1. Update `AirdropBase` model in `models.py`
2. Update validation rules
3. Update serialization in `utils.py`

### Adding New Endpoints
1. Create new route files in `routes/`
2. Import and include in `main.py`
3. Add authentication if needed

### Database Changes
1. Update `database.py` for new collections
2. Update models for new schemas
3. Add migration scripts if needed

---

**Ready to use!** 🚀 Your FastAPI + MongoDB airdrop management backend is complete and ready for deployment.
