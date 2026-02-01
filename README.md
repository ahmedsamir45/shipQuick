# 🚀 Bulk Shipping Label Platform - Frontend

Modern, responsive React + TypeScript + Tailwind CSS frontend for bulk shipping label creation.

## ✨ Features

- ✅ **4-Step Wizard** - Upload → Review → Shipping → Purchase
- ✅ **CSV Upload** - Drag & drop with validation and progress tracking
- ✅ **Interactive Review Table** - Edit, delete, bulk operations
- ✅ **Shipping Service Selection** - Auto-assignment with manual override
- ✅ **PDF Label Generation** - Download shipping labels
- ✅ **Responsive Design** - Mobile-friendly with hamburger menu
- ✅ **Custom Confirmation Dialogs** - Professional UI for confirmations
- ✅ **Real-time Updates** - Instant feedback on all operations
- ✅ **TypeScript** - Type-safe development
- ✅ **Tailwind CSS** - Modern, utility-first styling

## 🛠️ Tech Stack

- **React** 18.3.1
- **TypeScript** 5.6.2
- **Vite** 6.0.7 (Build tool & dev server)
- **Tailwind CSS** 3.4.17 (Styling)
- **Axios** 1.7.9 (HTTP client)
- **Lucide React** (Icons)

## 🚀 Quick Start

### Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: **http://localhost:5173**

**Backend Required:** Ensure backend is running at `http://localhost:8000`

## 🚀 Deployment to Vercel

This frontend is ready to deploy to Vercel.

**Complete Guide:** See [../VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md)

**Quick Steps:**

1. Push code to GitHub
2. Import to Vercel
3. Set Root Directory: `frontend`
4. Set Environment Variable:
   ```
   VITE_API_BASE_URL=https://your-backend.koyeb.app/api
   ```
5. Deploy!

## 🔗 Backend Integration

Backend deploys to Koyeb: `https://your-app.koyeb.app`

**See:**
- [../KOYEB_DEPLOYMENT.md](../KOYEB_DEPLOYMENT.md) - Deploy backend
- [../VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) - Deploy frontend

---

**Built with ❤️ using React + TypeScript + Tailwind CSS**
