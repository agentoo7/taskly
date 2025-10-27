import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');

    // Check page is loaded
    await expect(page.getByRole('heading', { name: /welcome to taskly/i })).toBeVisible();

    // Navigate to login
    const loginLink = page.getByRole('link', { name: /sign in|login/i });
    if (await loginLink.isVisible()) {
      await loginLink.click();
      await page.waitForURL(/login/);
    }
  });

  test('should show 404 page for non-existent routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist-12345');

    // Should show 404 page
    await expect(page.getByText(/404/i)).toBeVisible();
    await expect(page.getByText(/not found/i)).toBeVisible();
  });

  test('should have working back navigation', async ({ page }) => {
    await page.goto('/');
    await page.goto('/login');

    await page.goBack();
    await expect(page).toHaveURL('/');
  });
});
