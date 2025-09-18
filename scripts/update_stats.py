import os
import requests
from collections import defaultdict
import re

# --- Environment Variables ---
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = "WARlord05"  # Your GitHub username

# --- Constants ---
API_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
README_PATH = "README.md"
START_COMMENT = ""
END_COMMENT = ""

def get_repos():
    """Fetch all repositories for the user."""
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

def generate_stats_markdown(lang_stats):
    """Generate Markdown text for the stats."""
    if not lang_stats:
        return ""
    
    total_bytes = sum(lang_stats.values())
    top_langs = sorted(lang_stats.items(), key=lambda item: item[1], reverse=True)[:5]

    markdown = "#### 💻 Top Languages\n\n"
    markdown += "```text\n"
    for lang, bytes_count in top_langs:
        percentage = (bytes_count / total_bytes) * 100
        bar = "█" * int(percentage / 4) + "░" * (25 - int(percentage / 4))
        markdown += f"{lang.ljust(15)} {bar} {percentage:.2f}%\n"
    markdown += "```\n"
    return markdown

def update_readme(stats_markdown):
    """Update the README.md file with the new stats."""
    with open(README_PATH, "r") as f:
        content = f.read()

    # Use regex to find and replace the content between comments
    pattern = f"{START_COMMENT}(.*){END_COMMENT}"
    new_content = re.sub(pattern, f"{START_COMMENT}\n{stats_markdown}\n{END_COMMENT}", content, flags=re.DOTALL)

    with open(README_PATH, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set in environment variables.")
    
    print("Fetching repository data...")
    user_repos = get_repos()
    
    print("Calculating language statistics...")
    language_stats = get_language_stats(user_repos)
    
    print("Generating new stats markdown...")
    stats_md = generate_stats_markdown(language_stats)
    
    print("Updating README.md...")
    update_readme(stats_md)
    
    print("✅ README update complete.")