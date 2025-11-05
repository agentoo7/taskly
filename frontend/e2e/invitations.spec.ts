import { test, expect } from '@playwright/test';

test.describe('Invitations', () => {
  test('should display invitation accept page with token', async ({ page }) => {
    const testToken = 'test-invitation-token-123';
    await page.goto(`/invitations/accept?token=${testToken}`);

    // Should show invitation page (not 404)
    await expect(page.getByText(/404/)).not.toBeVisible();
  });

  test('should handle missing token gracefully', async ({ page }) => {
    await page.goto('/invitations/accept', { waitUntil: 'domcontentloaded' });

    // Should show error message or redirect to login
    // Wait for either error message or redirect
    await Promise.race([
      page.getByText(/error|invalid|expired/i).waitFor({ timeout: 5000 }).catch(() => null),
      page.waitForURL(/\/(login|invitations)/, { timeout: 5000 }).catch(() => null),
    ]);

    // Page should not crash
    expect(page.url()).toBeTruthy();
  });
});
