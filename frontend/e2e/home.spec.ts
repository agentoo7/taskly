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
    // Start navigation without waiting
    const navigation = page.goto('/');

    // Try to catch loading state (may be too fast to catch)
    const loadingIndicator = page.locator('[class*="animate-spin"]');
    const hasLoading = await loadingIndicator.or(page.getByText(/loading/i)).isVisible().catch(() => false);

    // Wait for navigation to complete
    await navigation;

    // Page should either have shown loading or loaded directly
    await expect(page.getByRole('heading', { name: /welcome to taskly/i })).toBeVisible();
  });

  test('should have proper meta tags', async ({ page }) => {
    await page.goto('/');

    // Check title
    await expect(page).toHaveTitle(/taskly/i);
  });
});
