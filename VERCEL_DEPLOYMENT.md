# Vercel Deployment Guide

This guide will help you deploy your shipping platform frontend to Vercel and connect it to your backend.

## Prerequisites

- Vercel account (sign up at https://vercel.com)
- Backend deployed and accessible (e.g., on a VPS, Railway, or cloud provider)
- Backend URL ready

## Step 1: Prepare Frontend for Deployment

The frontend is already configured to use environment variables. The API client uses `VITE_API_BASE_URL` to determine the backend URL.

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts and set up your project.

### Option B: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository (GitHub, GitLab, or Bitbucket)
3. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

## Step 3: Configure Environment Variables in Vercel

After deployment, configure the environment variable:

1. Go to your project settings in Vercel Dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variable:

| Name | Value | Environment |
|------|-------|-------------|
| `VITE_API_BASE_URL` | `https://your-backend-domain.com/api` | Production |

**Important:** Replace `your-backend-domain.com` with your actual backend URL.

## Step 4: Update Backend CORS Settings

After deploying to Vercel, you'll receive a deployment URL (e.g., `https://your-app.vercel.app`).

1. Update your backend `.env` file with the Vercel URL:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

2. Add your backend domain to `ALLOWED_HOSTS`:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,your-backend-domain.com
```

3. Restart your backend server to apply changes.

## Step 5: Redeploy Frontend

After updating the environment variables in Vercel:

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click **Redeploy** to rebuild with the new environment variables

## Vercel Configuration (Optional)

Create a `vercel.json` file in the frontend directory for additional configuration:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

This enables:
- Client-side routing (SPA)
- Asset caching for better performance

## Environment-Specific URLs

Vercel provides multiple URLs for your deployment:

1. **Production URL:** `https://your-app.vercel.app`
2. **Git Branch URLs:** `https://your-app-git-branch.vercel.app`
3. **Custom Domain:** Configure in Vercel settings

Make sure to add ALL relevant URLs to your backend's `CORS_ALLOWED_ORIGINS`.

## Testing the Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Open browser console (F12) and check for:
   - API requests going to correct backend URL
   - No CORS errors
   - Successful API responses

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Verify backend `CORS_ALLOWED_ORIGINS` includes your Vercel URL
2. Check that backend is running and accessible
3. Ensure `VITE_API_BASE_URL` is set correctly in Vercel

### API Not Found (404 Errors)

1. Check `VITE_API_BASE_URL` in Vercel environment variables
2. Verify backend URL is correct and includes `/api` path
3. Test backend directly: `curl https://your-backend-domain.com/api/sessions/`

### Build Failures

1. Check build logs in Vercel dashboard
2. Ensure all dependencies are in `package.json`
3. Verify Node.js version compatibility

## Custom Domain (Optional)

To use a custom domain:

1. Go to **Settings** → **Domains** in Vercel
2. Add your domain
3. Update DNS records as instructed
4. Add custom domain to backend `CORS_ALLOWED_ORIGINS`

## Continuous Deployment

Vercel automatically redeploys when you push to your Git repository:

- **Main branch** → Production deployment
- **Other branches** → Preview deployments

Each preview deployment gets a unique URL for testing.

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] `VITE_API_BASE_URL` set in Vercel environment variables
- [ ] Backend `CORS_ALLOWED_ORIGINS` includes Vercel URL
- [ ] Backend `ALLOWED_HOSTS` includes backend domain
- [ ] Backend `DEBUG=False` in production
- [ ] Backend `SECRET_KEY` is secure (not default)
- [ ] Test API calls from Vercel deployment
- [ ] Check browser console for errors
- [ ] Verify all features work (upload, review, shipping, purchase)

## Support

For Vercel-specific issues, check:
- Vercel Documentation: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
