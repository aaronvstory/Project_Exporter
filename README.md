# Project File Export Tool
![image](https://github.com/user-attachments/assets/4cf70ba3-1237-47e7-9028-4e975c072e08)

![image](https://github.com/user-attachments/assets/33fa68ad-629e-418c-85ec-b6caecdb87ce)


## Introduction

This is a project file export tool developed using PyQt5. It allows users to drag and drop or select project folders into the tool window, then automatically generates a text file containing the project's file structure and specific content (optional).

The tool aims to help developers directly pass project details to LLMs through context.

This project's code was almost entirely written by GPT-4 and Claude 3.5 Sonnet, with me only providing requirements and suggestions.

## Features

- Automatically generates project file structure tree
- Extracts code content from each file and writes to output file (optional)
- Uses XML tags to wrap file content for better LLM readability
- Places exported text files in the imported project directory
- Real-time display of export status and output file path

## How to Use

1. Go to [Releases](https://github.com/CookSleep/Project_Exporter/releases) page
2. Download the latest version of `Project_Exporter.zip`
3. Extract `Project_Exporter.zip`
4. Double-click to run `Project File Export Tool.exe`
5. Drag the project folder into the program window or click "Select Folder" to choose the folder to export
6. After completion, check the output file in the project directory (also shown in the output box)
7. Copy and paste the entire text into the LLM's context window to continue your project research journey with the LLM

## Contributing

If you have any suggestions or comments about this project, feel free to submit an Issue or Pull Request.

