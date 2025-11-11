#!/usr/bin/env python3
"""
Generate a social media preview image for the MSTR Goes Boom app.
Creates a 1200x630 PNG image optimized for WhatsApp, Twitter, Facebook, etc.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patheffects import withStroke

def create_preview_image():
    # Create figure with exact social media dimensions (1200x630)
    fig = plt.figure(figsize=(12, 6.3), facecolor='#0e1117')
    ax = fig.add_subplot(111)
    
    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Dark background
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    # Add bomb emoji or icon at the top
    ax.text(0.5, 0.75, '🧨', 
            fontsize=120, 
            ha='center', 
            va='center',
            color='white')
    
    # Main title
    title_text = ax.text(0.5, 0.50, 'MSTR Goes Boom?', 
                         fontsize=52, 
                         ha='center', 
                         va='center',
                         color='#ff4b4b',
                         weight='bold',
                         family='sans-serif')
    
    # Add white stroke/outline to title for better readability
    title_text.set_path_effects([
        withStroke(linewidth=3, foreground='white', alpha=0.3)
    ])
    
    # Subtitle
    subtitle_text = ax.text(0.5, 0.35, 
                           'When Does MicroStrategy\'s\nBitcoin Bet Collapse?', 
                           fontsize=28, 
                           ha='center', 
                           va='center',
                           color='white',
                           weight='normal',
                           family='sans-serif',
                           linespacing=1.5)
    
    # Call to action
    cta_text = ax.text(0.5, 0.15, 
                       '▶  Run Interactive Scenarios  ◀', 
                       fontsize=22, 
                       ha='center', 
                       va='center',
                       color='#ffa500',
                       weight='bold',
                       family='monospace',
                       style='italic')
    
    # Add decorative elements - danger stripes at bottom
    stripe_height = 0.05
    num_stripes = 30
    for i in range(num_stripes):
        x = i / num_stripes
        color = '#ff4b4b' if i % 2 == 0 else '#ffff00'
        rect = mpatches.Rectangle((x, 0), 1/num_stripes, stripe_height, 
                                   facecolor=color, 
                                   edgecolor='none',
                                   alpha=0.6)
        ax.add_patch(rect)
    
    # Add subtle grid lines in background (like a financial chart)
    for y in [0.2, 0.4, 0.6, 0.8]:
        ax.axhline(y=y, color='#262730', linewidth=0.5, alpha=0.3, linestyle='--')
    
    for x in [0.2, 0.4, 0.6, 0.8]:
        ax.axvline(x=x, color='#262730', linewidth=0.5, alpha=0.3, linestyle='--')
    
    # Tight layout
    plt.tight_layout(pad=0)
    
    # Save with high DPI for crisp social media previews
    plt.savefig('preview.png', 
                dpi=100, 
                facecolor='#0e1117', 
                edgecolor='none',
                bbox_inches='tight',
                pad_inches=0)
    
    print("✅ Preview image generated: preview.png")
    print("   Dimensions: 1200x630 pixels")
    print("   Optimized for WhatsApp, Twitter, Facebook, LinkedIn")
    print("\n📤 Next steps:")
    print("   1. Review the preview.png file")
    print("   2. Commit and push it to your GitHub repo")
    print("   3. Redeploy your Streamlit app")
    print("   4. Test the link preview on WhatsApp!")

if __name__ == '__main__':
    create_preview_image()

