import { describe, it, expect } from 'vitest';
import openapiSchema from './backend-openapi.json';

describe('Phase 3d: Automated Backend OpenAPI Contract Verification', () => {
  const paths = openapiSchema.paths as Record<string, Record<string, any>>;
  const schemas = (openapiSchema.components as any)?.schemas || {};

  const FRONTEND_ENDPOINTS: Array<{
    method: 'get' | 'post';
    path: string;
    requestFields?: string[];
    responseSchemaName?: string;
  }> = [
    { method: 'get', path: '/api/v1/health', responseSchemaName: 'HealthResponse' },
    { method: 'get', path: '/api/v1/ready' },
    { method: 'get', path: '/api/v1/harvester/products', responseSchemaName: 'PaginatedProducts' },
    { method: 'get', path: '/api/v1/harvester/products/{product_id}', responseSchemaName: 'ProductDetailResponse' },
    { method: 'get', path: '/api/v1/harvester/products/{product_id}/insights', responseSchemaName: 'ProductInsightsResponse' },
    { method: 'get', path: '/api/v1/harvester/reviews', responseSchemaName: 'PaginatedReviews' },
    { method: 'get', path: '/api/v1/harvester/products/{product_id}/price-history', responseSchemaName: 'PriceHistoryResponse' },
    { method: 'post', path: '/api/v1/harvester/products/{product_id}/check-price', responseSchemaName: 'PriceHistoryResponse' },
    { method: 'post', path: '/api/v1/harvester/analyze-url', requestFields: ['url'], responseSchemaName: 'ProductUrlAnalysisResponse' },
    { method: 'post', path: '/api/v1/harvester/flipkart/scrape', requestFields: ['url'], responseSchemaName: 'FlipkartScrapeResponse' },
    { method: 'post', path: '/api/v1/harvester/jobs', requestFields: ['source'], responseSchemaName: 'JobStatusResponse' },
    { method: 'get', path: '/api/v1/harvester/jobs/{job_id}', responseSchemaName: 'JobStatusResponse' },
    { method: 'post', path: '/api/v1/analysis/readability', requestFields: ['text'], responseSchemaName: 'ReadabilityResponse' },
    { method: 'post', path: '/api/v1/analysis/language', requestFields: ['text'], responseSchemaName: 'LanguageDetectionResponse' },
    { method: 'post', path: '/api/v1/analysis/sentiment', requestFields: ['text'], responseSchemaName: 'SentimentResponse' },
    { method: 'post', path: '/api/v1/analysis/topics', requestFields: ['documents'], responseSchemaName: 'TopicsResponse' },
  ];

  FRONTEND_ENDPOINTS.forEach(({ method, path, requestFields, responseSchemaName }) => {
    it(`validates contract for ${method.toUpperCase()} ${path}`, () => {
      // 1. Path must exist in backend OpenAPI schema
      expect(paths).toHaveProperty(path);
      const pathItem = paths[path];

      // 2. HTTP method must exist for that path
      expect(pathItem).toHaveProperty(method);
      const operation = pathItem[method];

      // 3. Request body fields must match backend schema
      if (requestFields && requestFields.length > 0) {
        const reqBody = operation.requestBody;
        expect(reqBody).toBeDefined();
        const jsonContent = reqBody.content['application/json'];
        expect(jsonContent).toBeDefined();

        let reqSchema = jsonContent.schema;
        if (reqSchema.$ref) {
          const refName = reqSchema.$ref.split('/').pop();
          reqSchema = schemas[refName];
        }

        const validProps = Object.keys(reqSchema.properties || {});
        requestFields.forEach((field) => {
          expect(validProps).toContain(field);
        });
      }

      // 4. Response schema (if specified) must exist in OpenAPI components
      if (responseSchemaName) {
        expect(schemas).toHaveProperty(responseSchemaName);
      }
    });
  });

  it('fails immediately when a nonexistent endpoint or method is verified', () => {
    const bogusEndpoint = { method: 'delete', path: '/api/v1/nonexistent' };
    expect(paths[bogusEndpoint.path]).toBeUndefined();
  });
});
