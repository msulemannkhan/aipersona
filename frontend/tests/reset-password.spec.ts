import { expect, test } from "@playwright/test"
import { findLastEmail } from "./utils/mailcatcher"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser, signUpNewUser } from "./utils/user"

test.use({ storageState: { cookies: [], origins: [] } })

test("Password Recovery title is visible", async ({ page }) => {
  await page.goto("/recover-password")

  await expect(
    page.getByRole("heading", { name: "Password Recovery" }),
  ).toBeVisible()
})

test("Input is visible, empty and editable", async ({ page }) => {
  await page.goto("/recover-password")

  await expect(page.getByPlaceholder("Email")).toBeVisible()
  await expect(page.getByPlaceholder("Email")).toHaveText("")
  await expect(page.getByPlaceholder("Email")).toBeEditable()
})

test("Continue button is visible", async ({ page }) => {
  await page.goto("/recover-password")

  await expect(page.getByRole("button", { name: "Continue" })).toBeVisible()
})

test("User can reset password successfully using the link", async ({
  page,
  request,
}) => {
  const fullName = "Test User"
  const email = randomEmail()
  const password = randomPassword()
  const newPassword = randomPassword()

  // Sign up a new user
  await signUpNewUser(page, fullName, email, password)

  await page.goto("/recover-password")
  await page.getByPlaceholder("Email").fill(email)

  await page.getByRole("button", { name: "Continue" }).click()

  const emailData = await findLastEmail({
    request,
    filter: (e) => e.recipients.includes(`<${email}>`),
    timeout: 5000,
  })

  const mailcatcherUrl = `${process.env.MAILCATCHER_HOST}/messages/${emailData.id}.html`

  // Find reset password email and click the link
  await page.goto(mailcatcherUrl);
  await page.waitForSelector("tr");
  await page.click("tr");
  await page.waitForSelector("iframe");
  const iframeContent = await page.frameLocator("iframe").locator("body");
  const link = await iframeContent.locator("a").getAttribute("href");
  if (link) {
    let url = link;
    // Replace the href from backend with the frontend URL
    url = url!.replace("http://localhost/", "http://localhost:19100/")
    await page.goto(url);
  }

  await page.getByPlaceholder("New Password").fill(newPassword)
  await page.getByPlaceholder("Confirm Password").fill(newPassword)
  await page.getByRole("button", { name: "Reset Password" }).click()
  await expect(page.locator("text=Your password has been successfully reset.")).toBeVisible();

  // Check if the user is able to login with the new password
  await logInUser(page, email, newPassword)
})

test("Expired or invalid reset link", async ({ page }) => {
  const password = randomPassword()
  const invalidUrl = "/reset-password?token=invalidtoken"

  await page.goto(invalidUrl)

  await page.getByPlaceholder("New Password").fill(password)
  await page.getByPlaceholder("Confirm Password").fill(password)
  await page.getByRole("button", { name: "Reset Password" }).click()

  await expect(page.getByText("Invalid token")).toBeVisible()
})

test("Weak new password validation", async ({ page, request }) => {
  const fullName = "Test User"
  const email = randomEmail()
  const password = randomPassword()
  const weakPassword = "123"

  // Sign up a new user
  await signUpNewUser(page, fullName, email, password)

  await page.goto("/recover-password")
  await page.getByPlaceholder("Email").fill(email)
  await page.getByRole("button", { name: "Continue" }).click()

  const emailData = await findLastEmail({
    request,
    filter: (e) => e.recipients.includes(`<${email}>`),
    timeout: 5000,
  })

  const mailcatcherUrl = `${process.env.MAILCATCHER_HOST}/messages/${emailData.id}.html`

  // Find reset password email and click the link
  await page.goto(mailcatcherUrl);
  await page.waitForSelector("tr");
  await page.click("tr");
  await page.waitForSelector("iframe");
  const iframeContent2 = await page.frameLocator("iframe").locator("body");
  const link2 = await iframeContent2.locator("a").getAttribute("href");
  if (link2) {
    let url = link2;
    // Replace the href from backend with the frontend URL
    url = url!.replace("http://localhost/", "http://localhost:19100/")
    await page.goto(url);
  }

  await page.getByPlaceholder("New Password").fill(weakPassword)
  await page.getByPlaceholder("Confirm Password").fill(weakPassword)
  await page.getByRole("button", { name: "Reset Password" }).click()

  await expect(
    page.getByText("Password must be at least 8 characters"),
  ).toBeVisible()
})
