

## Alpha Insights

### Create Alpha Insight
api: https://gfiresearch.dev
- **Endpoint:** `POST /api/alpha-insights`
- **Description:** Creates a new Alpha Insight.
- **Body:** `AlphaInsightCreate` model.
- **Example:**
  ```bash
  curl -X POST "https://gfiresearch.dev/api/alpha-insights" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Insight Title",
    "category": "DeFi",
    "token": "ALPHA",
    "platform": "Ethereum",
    "raised": "10M",
    "description": "A detailed description of the insight.",
    "date": "2025-10-16",
    "imageUrl": "http://example.com/image.png",
    "url": "http://example.com/insight-details"
  }'
  ```

### Get All Alpha Insights

- **Endpoint:** `GET /api/alpha-insights`
- **Description:** Retrieves a list of all Alpha Insights.

### Update Alpha Insight

- **Endpoint:** `PUT /api/alpha-insights/{id}`
- **Description:** Updates an existing Alpha Insight.
- **Body:** `AlphaInsightUpdate` model.
- **Example:**
  ```bash
  curl -X PUT "https://gfiresearch.dev/api/alpha-insights/{INSIGHT_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "An Updated Insight Title"
  }'
  ```

### Delete Alpha Insight

- **Endpoint:** `DELETE /api/alpha-insights/{id}`
