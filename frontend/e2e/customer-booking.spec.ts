import { expect, test } from '@playwright/test';

test('customer signs in, books an available slot, views it, and cancels it', async ({ page }) => {
  await page.goto('/login');
  await page.locator('input[type="email"]').fill('customer@example.com');
  await page.locator('input[type="password"]').fill('DemoPass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/bookings$/);

  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Available venues' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Pune Sports Arena' })).toBeVisible();
  await page.getByRole('button', { name: 'View slots' }).first().click();

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const targetDate = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth() + 1).padStart(2, '0')}-${String(tomorrow.getDate()).padStart(2, '0')}`;
  await page.locator('input[type="date"]').fill(targetDate);

  const availableSlot = page.locator('.slot:not([disabled])').first();
  await expect(availableSlot).toBeVisible();
  await availableSlot.click();
  await page.getByRole('button', { name: 'Confirm booking' }).click();

  const confirmation = page.getByText(/Confirmed: SPT-/);
  await expect(confirmation).toBeVisible();
  const bookingReference = (await confirmation.textContent())?.replace('Confirmed: ', '').trim();
  expect(bookingReference).toBeTruthy();

  await page.goto('/bookings');
  const booking = page.locator('article.card').filter({ hasText: bookingReference! });
  await expect(booking).toBeVisible();
  await booking.getByRole('button', { name: 'Cancel' }).click();
  await expect(booking.getByText('CANCELLED')).toBeVisible();
});

test('protected customer, owner, and admin pages explain missing authentication', async ({ page }) => {
  for (const route of ['/bookings', '/owner', '/admin']) {
    await page.goto(route);
    await expect(page.locator('p[role="alert"]')).toContainText('session is missing or expired');
  }
});

test('discovery reports when the API is unavailable', async ({ page }) => {
  await page.route('**/api/**', (route) => route.abort());
  await page.goto('/');
  await expect(page.locator('p[role="alert"]')).toContainText('TurfMate API is unavailable');
});