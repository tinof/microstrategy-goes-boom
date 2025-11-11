# GitHub Repository Setup Instructions

Follow these steps to create a new GitHub repository and push your code:

## Option 1: Create Repository via GitHub Web Interface (Recommended)

1. **Go to GitHub**:
   - Visit https://github.com/new
   - Or click the "+" icon in the top right → "New repository"

2. **Configure the repository**:
   - **Repository name**: `microstrategy-goes-boom`
   - **Description**: "A toy model of MicroStrategy's leveraged Bitcoin strategy - interactive Streamlit app"
   - **Visibility**: Choose Public or Private
   - **Important**: Do NOT initialize with README, .gitignore, or license (we already have these)

3. **Create the repository** (click the green button)

4. **Initialize and push your local code**:
   ```bash
   cd /Users/konstantinosfotiou/Documents/GitHub/coinmotion/microstrategy-goes-boom
   
   # Initialize git repository
   git init
   
   # Add all files
   git add .
   
   # Make initial commit
   git commit -m "Initial commit: MicroStrategy Ponzi-style model with Streamlit"
   
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/microstrategy-goes-boom.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

## Option 2: Create Repository via GitHub CLI (if you have gh installed)

```bash
cd /Users/konstantinosfotiou/Documents/GitHub/coinmotion/microstrategy-goes-boom

# Initialize git
git init
git add .
git commit -m "Initial commit: MicroStrategy Ponzi-style model with Streamlit"

# Create repo and push (will prompt for public/private choice)
gh repo create microstrategy-goes-boom --source=. --push
```

## Post-Setup Steps

### 1. Test Locally Before Pushing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### 2. Optional: Deploy to Streamlit Cloud

After pushing to GitHub, you can deploy for free:

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `microstrategy-goes-boom`
5. Main file path: `app.py`
6. Click "Deploy"

Your app will be live at: `https://YOUR_USERNAME-microstrategy-goes-boom.streamlit.app`

### 3. Add Topics/Tags on GitHub

After creating the repo, add relevant topics on GitHub:
- streamlit
- bitcoin
- financial-modeling
- python
- data-visualization
- microstrategy
- simulation

### 4. Update README

If you want to customize the README.md:
- Add screenshots of the app
- Update the GitHub URL with your actual username
- Add your own contact info or social links

## Troubleshooting

### If you get authentication errors:

**HTTPS (easier)**:
- GitHub will prompt for username and Personal Access Token (PAT)
- Generate PAT at: https://github.com/settings/tokens
- Use PAT as password when prompted

**SSH (more secure, but requires setup)**:
```bash
# Use SSH URL instead
git remote set-url origin git@github.com:YOUR_USERNAME/microstrategy-goes-boom.git
```

### If you need to change remote URL:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/microstrategy-goes-boom.git
```

### If you accidentally initialized with files:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Next Steps

- ⭐ Star your own repo
- 📝 Add project to your GitHub profile
- 🚀 Deploy to Streamlit Cloud (free!)
- 🔗 Share with friends/colleagues
- 💡 Iterate and improve the model

Enjoy! 🎉

