# Binance Alpha Backend API Documentation

This document provides comprehensive information about the Binance Alpha Backend API endpoints, their parameters, request/response formats, and examples.

## Base URL

```
https://gfiresearch.dev
```

## Authentication

Admin endpoints require authentication. Currently, a simple authentication mechanism is used for testing purposes.

## Public Endpoints

### Get Airdrops

Retrieve a list of airdrops filtered by range.

**URL**: `/api/airdrops`

**Method**: `GET`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| range | string | No | "all" | Filter airdrops by range. Possible values: "today", "upcoming", "all" |

**Response**:

```json
{
  "items": [
    {
      "id": "string",
      "project": "string",
      "alias": "string",
      "points": null,
      "amount": null,
      "event_date": "2025-10-08",
      "event_time": "14:00:00",
      "time_iso": "2025-10-08T14:00:00+07:00",
      "timezone": "Asia/Ho_Chi_Minh",
      "phase": "string",
      "x": "string",
      "raised": 0,
      "source_link": "string",
      "created_at": "2025-10-08T07:00:00.000Z",
      "updated_at": "2025-10-08T07:00:00.000Z",
      "deleted": false
    }
  ],
  "etag": "string"
}
```

**Notes**:
- The API supports ETag caching. The client can send an `If-None-Match` header with the ETag value to get a 304 response if the content hasn't changed.
- Results are sorted by time_iso in descending order (newest first).
- Only non-deleted airdrops are returned.

**Example Request**:

```
GET https://gfiresearch.dev/api/airdrops?range=today
```

## Admin Endpoints

### Create Airdrop

Create a new airdrop.

**URL**: `/api/airdrops`

**Method**: `POST`

**Request Body**:

```json
{
  "project": "string",
  "alias": "string",
  "points": null,
  "amount": null,
  "event_date": "2025-10-08",
  "event_time": "14:00",
  "timezone": "Asia/Ho_Chi_Minh",
  "phase": "string",
  "x": "string",
  "raised": 0,
  "source_link": "string"
}
```

**Notes**:
- Provide the event date via `event_date` (`YYYY-MM-DD`). Supply `event_time` (`HH:MM` or `HH:MM:SS`) when you know the exact schedule; otherwise omit it.

**Response**:

```json
{
  "id": "string",
  "project": "string",
  "alias": "string",
  "points": null,
  "amount": null,
  "event_date": "2025-10-08",
  "event_time": "14:00:00",
  "time_iso": "2025-10-08T14:00:00+07:00",
  "timezone": "Asia/Ho_Chi_Minh",
  "phase": "string",
  "x": "string",
  "raised": 0,
  "source_link": "string",
  "created_at": "2025-10-08T07:00:00.000Z",
  "updated_at": "2025-10-08T07:00:00.000Z",
  "deleted": false
}
```

**Status Code**: 201 Created

### Update Airdrop

Update an existing airdrop.

**URL**: `/api/airdrops/{id}`

**Method**: `PUT`

**URL Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | The ID of the airdrop to update |

**Request Body**:

```json
{
  "project": "string",
  "alias": "string",
  "points": null,
  "amount": null,
  "event_date": "2025-10-08",
  "event_time": "14:00",
  "timezone": "Asia/Ho_Chi_Minh",
  "phase": "string",
  "x": "string",
  "raised": 0,
  "source_link": "string"
}
```

**Notes**:
- All fields are optional. Only provided fields will be updated.

**Response**:

```json
{
  "id": "string",
  "project": "string",
  "alias": "string",
  "points": null,
  "amount": null,
  "event_date": "2025-10-08",
  "event_time": "14:00:00",
  "time_iso": "2025-10-08T14:00:00+07:00",
  "timezone": "Asia/Ho_Chi_Minh",
  "phase": "string",
  "x": "string",
  "raised": 0,
  "source_link": "string",
  "image_url": "srtring",
  "created_at": "2025-10-08T07:00:00.000Z",
  "updated_at": "2025-10-08T07:00:00.000Z",
  "deleted": false
}
```

### Delete Airdrop

Permanently delete an airdrop.

**URL**: `/api/airdrops/{id}`

**Method**: `DELETE`

**URL Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | The ID of the airdrop to delete |

**Response**:

Empty response with status code 204 No Content.

### Get All Airdrops (Admin)

Retrieve all airdrops currently in the database.

**URL**: `/api/admin/airdrops`

**Method**: `GET`

**Response**:

```json
[
  {
    "id": "string",
    "project": "string",
    "alias": "string",
    "points": null,
    "amount": null,
    "event_date": "2025-10-08",
    "event_time": "14:00:00",
    "time_iso": "2025-10-08T14:00:00+07:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "phase": "string",
    "x": "string",
    "raised": 0,
    "source_link": "string",
    "created_at": "2025-10-08T07:00:00.000Z",
    "updated_at": "2025-10-08T07:00:00.000Z",
    "deleted": false
  }
]
```

### Get Deleted Airdrops (Legacy)

Legacy endpoint that previously returned soft-deleted airdrops. Since deletes are now permanent, this endpoint always returns an empty list.

**URL**: `/api/admin/airdrops/deleted`

**Method**: `GET`

**Response**:

```json
[]
```

## Data Models

### Airdrop

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes (in responses) | Unique identifier for the airdrop |
| project | string | Yes | Project name |
| alias | string | Yes | Project alias |
| points | number | No | Points value (optional, >= 0 when provided) |
| amount | number | No | Amount value (optional, >= 0 when provided) |
| event_date | string | Yes | Event date in `YYYY-MM-DD` format |
| event_time | string | No | Event time in `HH:MM` or `HH:MM:SS` format |
| time_iso | string | Yes (auto) | Combined ISO datetime generated from date/time/timezone |
| timezone | string | No | Timezone (e.g., "Asia/Ho_Chi_Minh"); defaults to UTC when omitted |
| phase | string | No | Project phase |
| x | string | No | X (Twitter) handle |
| raised | string | No | Amount raised |
| source_link | string | No | Source link |
| created_at | string | Yes (in responses) | Creation timestamp |
| updated_at | string | Yes (in responses) | Last update timestamp |
| deleted | boolean | Yes (in responses) | Deletion status |

## Error Responses

The API returns standard HTTP status codes to indicate success or failure:

- 200 OK: The request was successful
- 201 Created: A new resource was successfully created
- 204 No Content: The request was successful but there is no content to return
- 304 Not Modified: The resource hasn't changed since the last request
- 400 Bad Request: The request was invalid or cannot be served
- 404 Not Found: The resource could not be found
- 500 Internal Server Error: An error occurred on the server

Error response body:

```json
{
  "error": "string",
  "detail": "string"
}
```
