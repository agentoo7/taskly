import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should load the home page', async ({ page }) => {
    await page.goto('/');

    // Check for main heading
    await expect(page.getByRole('heading', { name: /welcome to taskly/i })).toBeVisible();

    // Check for description
    await expect(page.getByText(/task management with github integration/i)).toBeVisible();
  });

  test('should display loading state initially', async ({ page }) => {
    await page.goto('/');

    // Check for loading indicator or spinner
    const loadingIndicator = page.locator('[class*="animate-spin"]');
    await expect(loadingIndicator.or(page.getByText(/loading/i))).toBeVisible({ timeout: 5000 });
  });

  test('should have proper meta tags', async ({ page }) => {
    await page.goto('/');

    // Check title
    await expect(page).toHaveTitle(/taskly/i);
  });
});
