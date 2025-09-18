import os
import requests
from collections import defaultdict
import re

# --- Environment Variables & Constants ---
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = "WARlord05"  # Your GitHub username
API_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
SVG_PATH = "stats.svg"  # We will save to this SVG file

def get_repos():
    """Fetch all non-forked repositories for the user."""
    repos = []
    page = 1
    while True:
        response = requests.get(f"{API_URL}/users/{USERNAME}/repos?page={page}&per_page=100", headers=HEADERS)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repos: {response.content}")
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return [repo for repo in repos if not repo["fork"]]

def get_language_stats(repos):
    """Calculate language usage stats across all repositories."""
    lang_stats = defaultdict(int)
    for repo in repos:
        response = requests.get(repo["languages_url"], headers=HEADERS)
        if response.status_code == 200:
            for lang, bytes_count in response.json().items():
                lang_stats[lang] += bytes_count
    return lang_stats

def generate_stats_svg(lang_stats):
    """Generate the SVG card for the language stats with a similar design."""
    if not lang_stats:
        return "Could not fetch language stats."
    
    total_bytes = sum(lang_stats.values())
    top_langs = sorted(lang_stats.items(), key=lambda item: item[1], reverse=True)[:6] # Up to 6 languages for this layout

    # --- SVG Colors and Dimensions (tuned to match your example) ---
    colors = {
        "bg_dark": "#1F2937",        # Dark background color
        "border": "#4B5563",         # Border color
        "line": "#4B5563",           # Subtle line color for separators/grid
        "text_main": "#F3F4F6",      # Main text color (light)
        "text_sub": "#9CA3AF",       # Subdued text color
        "bar_bg": "#D1D5DB",         # Progress bar background (light gray)
        "bar_fill": "#6EE7B7"        # Bright green fill for bars
    }

    card_width = 700  # Increased width for better spacing
    card_height = 250 + (len(top_langs) - 5) * 40 # Adjust height based on number of languages
    
    # Base SVG structure with rounded rectangle border
    svg = f'''
    <svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="1" y="1" width="{card_width - 2}" height="{card_height - 2}" rx="8" ry="8" fill="{colors["bg_dark"]}" stroke="{colors["border"]}" stroke-width="2"/>

        <line x1="{card_width / 2 - 100}" y1="20" x2="{card_width / 2 - 100}" y2="60" stroke="{colors["line"]}" stroke-width="1"/>
        <line x1="{card_width / 2 + 100}" y1="20" x2="{card_width / 2 + 100}" y2="60" stroke="{colors["line"]}" stroke-width="1"/>
        
        <text x="{card_width / 2}" y="45" font-family="Segoe UI, sans-serif" font-size="24" font-weight="bold" fill="{colors["text_main"]}" text-anchor="middle">Top Languages</text>

        <line x1="20" y1="70" x2="{card_width - 20}" y2="70" stroke="{colors["line"]}" stroke-width="1" stroke-opacity="0.5"/>
        <line x1="20" y1="{card_height - 20}" x2="{card_width - 20}" y2="{card_height - 20}" stroke="{colors["line"]}" stroke-width="1" stroke-opacity="0.5"/>
        
        <line x1="{card_width / 4}" y1="70" x2="{card_width / 4}" y2="{card_height - 20}" stroke="{colors["line"]}" stroke-width="0.5" stroke-opacity="0.3"/>
        <line x1="{card_width / 2}" y1="70" x2="{card_width / 2}" y2="{card_height - 20}" stroke="{colors["line"]}" stroke-width="0.5" stroke-opacity="0.3"/>
        <line x1="{card_width * 3 / 4}" y1="70" x2="{card_width * 3 / 4}" y2="{card_height - 20}" stroke="{colors["line"]}" stroke-width="0.5" stroke-opacity="0.3"/>


        <g transform="translate(40, 95)"> '''

    # Loop to create progress bars for each language
    bar_spacing = 30 # Vertical space between bars
    max_bar_width = card_width - 160 # Max width for the bar itself, considering padding
    
    for i, (lang, bytes_count) in enumerate(top_langs):
        percentage = (bytes_count / total_bytes) * 100
        bar_fill_width = (percentage / 100) * max_bar_width # Actual fill width
        y_pos = i * bar_spacing

        svg += f'''
            <text x="0" y="{y_pos + 10}" font-family="Segoe UI, sans-serif" font-size="16" fill="{colors["text_main"]}">
                {lang}
            </text>
            
            <text x="{max_bar_width + 100}" y="{y_pos + 10}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="14" fill="{colors["text_sub"]}">
                {percentage:.1f}%
            </text>
            
            <rect x="120" y="{y_pos + 2}" width="{max_bar_width}" height="10" fill="{colors["bar_bg"]}" rx="5" ry="5"/>
            
            <rect x="120" y="{y_pos + 2}" width="{bar_fill_width}" height="10" fill="{colors["bar_fill"]}" rx="5" ry="5"/>
        '''
    
    # Closing tags
    svg += '''
        </g>
    </svg>
    '''
    return svg

def save_svg(svg_content):
    """Saves the SVG content to a file."""
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise ValueError("A GITHUB_TOKEN is required to run this script.")
    
    print("Fetching repository data...")
    user_repos = get_repos()
    
    print("Calculating language statistics...")
    language_stats = get_language_stats(user_repos)
    
    print("Generating new stats SVG...")
    stats_svg = generate_stats_svg(language_stats)
    
    print(f"Saving SVG to {SVG_PATH}...")
    save_svg(stats_svg)
    
    print("✅ SVG update complete.")
