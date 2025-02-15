import os
import requests

BASE_URL = "https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons"
ICON_DIR = "icons"

# Ensure icons directory exists
os.makedirs(ICON_DIR, exist_ok=True)

ICONS_TO_DOWNLOAD = {
    # Basic icons
    "folder.svg": "folder.svg",
    "file.svg": "file.svg",
    # Programming languages
    "python.svg": "python.svg",
    "javascript.svg": "javascript.svg",
    "typescript.svg": "typescript.svg",
    "html.svg": "html.svg",
    "css.svg": "css.svg",
    "java.svg": "java.svg",
    "cpp.svg": "cpp.svg",
    "csharp.svg": "csharp.svg",
    "go.svg": "go.svg",
    "rust.svg": "rust.svg",
    # Documentation
    "markdown.svg": "markdown.svg",
    "text.svg": "text.svg",
    "pdf.svg": "pdf.svg",
    "word.svg": "word.svg",
    # Data formats
    "json.svg": "json.svg",
    "xml.svg": "xml.svg",
    "yaml.svg": "yaml.svg",
    "csv.svg": "csv.svg",
    # Images
    "image.svg": "image.svg",
    "svg.svg": "svg.svg",
    # Config
    "config.svg": "settings.svg",
}

def download_icon(icon_name: str, save_as: str):
    """Download an icon from VSCode's repository."""
    url = f"{BASE_URL}/{icon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(ICON_DIR, save_as), "wb") as f:
            f.write(response.content)
        print(f"Downloaded {icon_name}")
    else:
        print(f"Failed to download {icon_name}: {response.status_code}")

def main():
    """Download all required icons."""
    print("Downloading VSCode icons...")
    for src, dst in ICONS_TO_DOWNLOAD.items():
        download_icon(src, dst)
    print("Icon download complete!")

if __name__ == "__main__":
    main()