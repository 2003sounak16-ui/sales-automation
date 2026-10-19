import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/api/pending', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'playwright-review-lead',
          company_name: 'Acme Corporation',
          industry: 'Technology',
          status: 'PENDING_REVIEW',
          ai_subject: 'A tailored introduction',
          ai_body: 'A sample message for the review queue.',
          contact_email: 'sales@example.com',
        },
      ]),
    }),
  );

  await page.route('**/api/leads', (route) => route.fulfill({ json: [] }));
  await page.route('**/api/timeline/**', (route) => route.fulfill({ json: [] }));
  await page.route('**/api/companies/trending', (route) =>
    route.fulfill({ json: [] }),
  );
});

test('loads the dashboard and opens the review queue', async ({ page }) => {
  const pendingResponse = page.waitForResponse((response) =>
    response.url().endsWith('/api/pending') && response.request().method() === 'GET',
  );
  await page.goto('http://localhost:3000/');

  await expect(
    page.getByRole('heading', { name: 'Sales Pipeline Dashboard' }),
  ).toBeVisible();
  await pendingResponse;

  await page.getByRole('button', { name: 'Review Queue' }).click();

  await expect(
    page.getByRole('heading', { name: 'Pitch Verification & Approval' }),
  ).toBeVisible({ timeout: 10000 });
  await expect(page.getByText('Acme Corporation', { exact: true })).toBeVisible();
});

