import os
import requests
from collections import defaultdict
import re

# --- Environment Variables & Constants ---
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = "WARlord05"  # Your GitHub username
API_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
SVG_PATH = "stats.svg"  # We will now save to an SVG file

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
    """Generate the SVG card for the language stats."""
    if not lang_stats:
        return "Could not fetch language stats."
    
    total_bytes = sum(lang_stats.values())
    top_langs = sorted(lang_stats.items(), key=lambda item: item[1], reverse=True)[:5]

    # --- SVG Template & Material 3 Inspired Colors ---
    # You can customize these colors, fonts, and sizes!
    colors = {
        "bg": "#FEF7FF",        # Background - Light Lavender
        "border": "#EADDFF",    # Border - Soft Lilac
        "text": "#1D1B20",      # Primary Text - Dark Slate
        "subtext": "#49454F",   # Secondary Text - Gray
        "bar_bg": "#E7E0EC",    # Progress Bar Background - Light Gray
        "bar_fill": ["#D0BCFF", "#AAC7FF", "#B9C2FFFF", "#93CCFFFF", "#81D4FAFF"] # Bar Fill Colors
    }
    
    svg_height = 165 + (len(top_langs) - 5) * 40
    
    # Header of the SVG
    svg = f'''
    <svg width="450" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{colors["bg"]}" stroke="{colors["border"]}" rx="16" ry="16"/>
        <g transform="translate(25, 35)">
            <text x="0" y="0" font-family="Segoe UI, sans-serif" font-size="18" font-weight="bold" fill="{colors["text"]}">Top Languages</text>
        </g>
        <g transform="translate(25, 60)">
    '''

    # Loop to create progress bars for each language
    for i, (lang, bytes_count) in enumerate(top_langs):
        percentage = (bytes_count / total_bytes) * 100
        bar_width = (percentage / 100) * 350
        y_pos = i * 25

        svg += f'''
            <text x="0" y="{y_pos}" font-family="Segoe UI, sans-serif" font-size="14" fill="{colors["text"]}">
                {lang}
            </text>
            <text x="400" y="{y_pos}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="12" fill="{colors["subtext"]}">
                {percentage:.2f}%
            </text>
            <rect x="0" y="{y_pos + 8}" width="400" height="8" fill="{colors["bar_bg"]}" rx="4" ry="4"/>
            <rect x="0" y="{y_pos + 8}" width="{bar_width}" height="8" fill="{colors["bar_fill"][i % len(colors["bar_fill"])]}" rx="4" ry="4"/>
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
