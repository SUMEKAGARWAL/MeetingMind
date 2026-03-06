# How to Get AWS Access Keys (Permanent Credentials)

## Step 1: Go to IAM Console

1. Open: https://console.aws.amazon.com/iam/home
2. Log in to your AWS account

## Step 2: Create Access Keys

1. In the left sidebar, click **"Users"**
2. Click on **your username**
3. Click the **"Security credentials"** tab
4. Scroll down to **"Access keys"** section
5. Click **"Create access key"**

## Step 3: Choose Use Case

1. Select **"Command Line Interface (CLI)"**
2. Check the box: "I understand the above recommendation..."
3. Click **"Next"**

## Step 4: Get Your Keys

1. You'll see:
   - **Access key ID** (starts with `AKIA...`)
   - **Secret access key** (long random string)
2. ⚠️ **IMPORTANT**: Copy both now! You can't see the secret key again!
3. Click **"Download .csv file"** (backup)
4. Click **"Done"**

## Step 5: Update .env File

Open `MeetingMind/.env` and update:

```bash
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=AKIA...your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
# Comment out or remove the AWS_SESSION_TOKEN line:
# AWS_SESSION_TOKEN=...
```

## Step 6: Test It

```bash
cd MeetingMind
python3 setup_aws.py
```

Should now work! ✅

---

## Security Best Practices

1. **Never commit** `.env` to git (it's already in `.gitignore`)
2. **Don't share** your secret key with anyone
3. **Rotate keys** periodically (create new, delete old)
4. **Use IAM policies** to limit permissions (principle of least privilege)

---

## Alternative: Use AWS SSO (Recommended for Organizations)

If your organization uses AWS SSO:

1. Go to your AWS SSO portal
2. Click on your account
3. Click **"Command line or programmatic access"**
4. Copy the credentials (includes session token)
5. Paste into `.env`

Note: SSO credentials expire after a few hours, but are more secure!

---

## Troubleshooting

### "Access Denied" errors
Your IAM user needs these permissions:
- S3: `s3:CreateBucket`, `s3:PutObject`, `s3:GetObject`
- Bedrock: `bedrock:*` (or specific permissions)
- IAM: `iam:CreateRole`, `iam:PutRolePolicy`
- OpenSearch Serverless: `aoss:*`

Ask your AWS administrator to grant these permissions.

### Can't create access keys
You might not have permission. Ask your AWS administrator to:
1. Create access keys for you, OR
2. Grant you `iam:CreateAccessKey` permission
