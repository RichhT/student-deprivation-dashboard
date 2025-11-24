# Deployment Guide: Student Disadvantage Dashboard

## Quick Deployment to Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub account
- Git installed locally (already done ✓)

### Step-by-Step Deployment

#### 1. Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **+** icon in top right → **New repository**
3. Fill in:
   - **Repository name**: `student-disadvantage-dashboard` (or your choice)
   - **Description**: "Interactive dashboard for analyzing student demographic and disadvantage data"
   - **Visibility**:
     - ⚠️ **Private** (recommended for school data)
     - OR **Public** (only if data is fully anonymized and you're comfortable sharing)
   - **Do NOT** initialize with README (we already have one)
4. Click **Create repository**

#### 2. Push Your Code to GitHub

Copy the commands from GitHub's "...or push an existing repository from the command line" section.

Or run these commands in your terminal (replace `YOUR_USERNAME` with your GitHub username):

```bash
cd /Users/richtaylor/Desktop/dev2/disadvantaged

# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/student-disadvantage-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

#### 3. Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Fill in:
   - **Repository**: Select your `student-disadvantage-dashboard` repo
   - **Branch**: `main`
   - **Main file path**: `dashboard.py`
5. Click **Deploy!**

**Done!** 🎉 Your dashboard will be live in ~2-3 minutes.

### Your Dashboard URL

After deployment, you'll get a URL like:
```
https://YOUR_USERNAME-student-disadvantage-dashboard.streamlit.app
```

You can share this URL with colleagues who need access.

## Alternative: Deploy to Other Platforms

### Option 2: Heroku
- More control but requires more setup
- Free tier available
- [Heroku Deployment Guide](https://docs.streamlit.io/deploy/tutorials/heroku)

### Option 3: AWS/Azure/GCP
- For enterprise deployments
- More expensive but highly scalable
- Full control over infrastructure

## Updating Your Dashboard

Whenever you make changes:

```bash
# Make your changes to dashboard.py or other files

# Commit and push
git add .
git commit -m "Description of changes"
git push

# Streamlit Cloud will automatically redeploy!
```

## Security Considerations

✅ **Done:**
- All student names removed from CSV files
- Only anonymized Student IDs retained
- Local virtual environment not committed (`.gitignore`)

⚠️ **Important:**
- If your repository is **private**, only people you give access can view it
- If **public**, anyone can see the code and data
- For school data, we recommend **private** repositories
- Streamlit Community Cloud apps can be password-protected (configure in settings)

## Adding Password Protection

After deployment on Streamlit Cloud:

1. Go to your app's dashboard on share.streamlit.io
2. Click **Settings**
3. Navigate to **Secrets**
4. Add authentication if needed using Streamlit's authentication components

## Troubleshooting

**Dashboard not loading?**
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has correct package versions
- Ensure `anonymised_data.csv` is committed to repository

**Data not showing?**
- Check that CSV file path in `dashboard.py` matches the repository structure
- Verify CSV encoding is UTF-8

## Support

For Streamlit deployment issues:
- [Streamlit Documentation](https://docs.streamlit.io/deploy)
- [Streamlit Community Forum](https://discuss.streamlit.io/)

---

**Current Status:**
✅ Git repository initialized
✅ Initial commit created
⏳ Awaiting GitHub repository creation and push
⏳ Awaiting Streamlit Cloud deployment
