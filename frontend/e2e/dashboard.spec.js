import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/api/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  );
});

test('loads the dashboard and opens the review queue', async ({ page }) => {
  await page.goto('/');

  await expect(
    page.getByRole('heading', { name: 'Sales Pipeline Dashboard' }),
  ).toBeVisible();

  await page.getByRole('button', { name: 'Review Queue' }).click();

  await expect(
    page.getByRole('heading', { name: 'Pitch Verification & Approval' }),
  ).toBeVisible();
});
