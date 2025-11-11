# 🚀 Deployment Guide: Improved Social Media Previews

## What Changed

### Files Modified:
1. **app.py**
   - Added `streamlit-javascript` import for meta tag injection
   - Updated page title to "MSTR Goes Boom: When Does MicroStrategy's Bitcoin Bet Collapse?"
   - Added JavaScript code to inject Open Graph meta tags into HTML head
   - More engaging intro text with emojis and clear call-to-action

2. **requirements.txt**
   - Added `streamlit-javascript>=0.1.5` dependency

3. **README.md**
   - Updated project structure documentation
   - Added social media preview section

### Files Created:
4. **generate_preview.py**
   - Script to generate optimized 1200x630 social media preview image

5. **preview.png**
   - Social media preview image (1200x630 pixels)
   - Optimized for WhatsApp, Twitter, Facebook, LinkedIn

## Deployment Steps

### 1. Commit and Push Changes

```bash
# Stage all changes
git add app.py requirements.txt README.md generate_preview.py preview.png DEPLOYMENT_GUIDE.md

# Commit with descriptive message
git commit -m "feat: improve social media link previews with Open Graph meta tags and custom preview image"

# Push to GitHub
git push origin main
```

### 2. Streamlit Cloud Will Auto-Redeploy

Once you push to GitHub, Streamlit Cloud will automatically:
- Detect the changes
- Install the new `streamlit-javascript` dependency
- Redeploy your app with the new meta tags

**Wait 2-3 minutes** for the deployment to complete.

### 3. Clear Social Media Caches

After deployment, you need to clear the cached previews:

#### WhatsApp
Unfortunately, WhatsApp doesn't provide a public cache-clearing tool. Options:
- Wait 24-48 hours for cache to expire naturally
- Share the link with a URL parameter: `?v=2` or `?refresh=1`
- Example: `https://microstrategy-goes-boom-neydsqr7vhwwa2wzgrdksj.streamlit.app/?v=2`

#### Facebook/Meta
1. Go to: https://developers.facebook.com/tools/debug/
2. Enter your app URL
3. Click "Scrape Again" to refresh cache

#### Twitter
1. Go to: https://cards-dev.twitter.com/validator
2. Enter your app URL
3. Click "Preview card"

#### LinkedIn
1. Go to: https://www.linkedin.com/post-inspector/
2. Enter your app URL
3. Click "Inspect"

### 4. Test the Preview

After clearing caches:
1. Share the link on WhatsApp to yourself or a test group
2. Check if you see:
   - Title: "MSTR Goes Boom: When Does MicroStrategy's Bitcoin Bet Collapse?"
   - Description with bomb emoji and call-to-action
   - Custom preview image (if GitHub URL is accessible)

## Troubleshooting

### Preview Image Not Showing

The preview image URL in the meta tags points to:
```
https://raw.githubusercontent.com/konstantinosfotiou/microstrategy-goes-boom/main/preview.png
```

**Verify:**
1. Check if the GitHub repo is public (required for raw.githubusercontent.com)
2. Verify the path is correct: `main` branch, root directory
3. Try accessing the image directly in your browser

If the repo is private, you have two options:
- Make the repo public
- Host the image on a public CDN (Imgur, Cloudinary, etc.) and update the URL in `app.py`

### Meta Tags Not Working

If social platforms still show a boring preview:

1. **Check browser console** for JavaScript errors
2. **Verify streamlit-javascript** installed correctly:
   ```bash
   pip list | grep streamlit-javascript
   ```

3. **Alternative approach** - Use Streamlit's native components:
   - Contact Streamlit Support to add custom meta tags
   - Use Streamlit Cloud's SEO settings (if available)

### Still Not Working?

The meta tag injection approach has limitations. For guaranteed results:

**Option A: Custom HTML Component**
Create a proper Streamlit component that injects meta tags server-side.

**Option B: Reverse Proxy**
Use a reverse proxy (like Cloudflare Workers) to inject meta tags before serving.

**Option C: Streamlit Support**
Contact Streamlit Cloud support to request native Open Graph tag support.

## Expected Result

After successful deployment and cache clearing, your WhatsApp preview should show:

```
┌─────────────────────────────────────┐
│  [Colorful Preview Image]           │
│                                     │
│  MSTR Goes Boom: When Does          │
│  MicroStrategy's Bitcoin Bet        │
│  Collapse?                          │
│                                     │
│  🧨 Interactive simulation: Test    │
│  different scenarios to see when... │
│                                     │
│  microstrategy-goes-boom-ney...     │
└─────────────────────────────────────┘
```

Much better than the boring default Streamlit preview!

## Notes

- **JavaScript Timing**: The `st_javascript()` call runs after page load, which may not be ideal for all social scrapers
- **Streamlit Limitations**: Streamlit doesn't officially support custom meta tags, so this is a workaround
- **Future-Proof**: Streamlit may add native Open Graph support in future versions

## Need Help?

If the preview still isn't working after following all steps, options include:
1. Try the URL parameter trick: `?v=2`
2. Use a URL shortener (bit.ly, tinyurl) which often triggers a re-scrape
3. Create a simple landing page that redirects to the Streamlit app with proper meta tags
4. Wait 48 hours for aggressive caches to expire

---

Good luck! 🚀

