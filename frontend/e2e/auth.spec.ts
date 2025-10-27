import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should navigate to login page', async ({ page }) => {
    await page.goto('/login');

    // Check for login page elements
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });

  test('should display GitHub OAuth button', async ({ page }) => {
    await page.goto('/login');

    // Look for GitHub sign-in button
    const githubButton = page.getByRole('button', { name: /github/i })
      .or(page.getByRole('link', { name: /github/i }));

    await expect(githubButton).toBeVisible();
  });

  test('should redirect to callback page after auth', async ({ page }) => {
    // This test would require mocking OAuth or using test credentials
    // For now, just check that the callback route exists
    await page.goto('/auth/callback?code=test123');

    // Should not show 404 page
    await expect(page.getByText(/404/)).not.toBeVisible();
  });
});
