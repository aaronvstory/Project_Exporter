import os

import requests

BASE_URL = "https://raw.githubusercontent.com/microsoft/vscode-codicons/main/src/icons"
ICON_DIR = "icons"

# Ensure icons directory exists
os.makedirs(ICON_DIR, exist_ok=True)

ICONS_TO_DOWNLOAD = {
    # Basic icons
    "folder.svg": "folder.svg",
    "file.svg": "file.svg",
    # Programming languages
    "symbol-method.svg": "python.svg",  # Using method symbol for Python
    "json.svg": "javascript.svg",  # JavaScript uses JSON icon
    "symbol-class.svg": "typescript.svg",  # TypeScript uses class symbol
    "browser.svg": "html.svg",  # HTML uses browser icon
    "symbol-color.svg": "css.svg",  # CSS uses color symbol
    "library.svg": "java.svg",  # Java uses library icon
    "debug.svg": "cpp.svg",  # C++ uses debug icon
    "vm.svg": "csharp.svg",  # C# uses VM icon
    "go-to-file.svg": "go.svg",  # Go uses go-to-file
    "tools.svg": "rust.svg",  # Rust uses tools
    # Documentation
    "markdown.svg": "markdown.svg",
    "text-size.svg": "text.svg",
    "output.svg": "pdf.svg",
    "file-binary.svg": "word.svg",
    # Data formats
    "bracket.svg": "json.svg",
    "code.svg": "xml.svg",
    "list-tree.svg": "yaml.svg",
    "list-flat.svg": "csv.svg",
    # Images
    "preview.svg": "image.svg",
    "type-hierarchy.svg": "svg.svg",
    # Config
    "settings-gear.svg": "config.svg",
}


def download_icon(icon_name: str, save_as: str):
    """Download an icon from VSCode's repository."""
    url = f"{BASE_URL}/{icon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(ICON_DIR, save_as), "wb") as f:
            f.write(response.content)
        print(f"Downloaded {icon_name} as {save_as}")
    else:
        print(f"Failed to download {icon_name}: {response.status_code}")


def main():
    """Download all required icons."""
    print("Downloading VSCode Codicons...")
    for src, dst in ICONS_TO_DOWNLOAD.items():
        download_icon(src, dst)
    print("Icon download complete!")


if __name__ == "__main__":
    main()
