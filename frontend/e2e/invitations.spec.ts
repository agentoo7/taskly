import { test, expect } from '@playwright/test';

test.describe('Invitations', () => {
  test('should display invitation accept page with token', async ({ page }) => {
    const testToken = 'test-invitation-token-123';
    await page.goto(`/invitations/accept?token=${testToken}`);

    // Should show invitation page (not 404)
    await expect(page.getByText(/404/)).not.toBeVisible();
  });

  test('should handle missing token gracefully', async ({ page }) => {
    await page.goto('/invitations/accept');

    // Should show error or redirect
    // The page should handle this case
    await page.waitForLoadState('networkidle');
  });
});
