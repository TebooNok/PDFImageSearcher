# PDF Image Extractor with Search

This project is a Python-based tool to extract images from a given PDF file and index the surrounding context of each image for subsequent search operations. Users can query the context in natural language, and the search results will present the related images. This tool supports both English and Chinese languages. For Chinese tokenization, the `jieba` library is used.

## Features
- Extracts images from PDF files.
- Indexes the context around each image.
- Allows querying using natural language.
- Supports both English and Chinese languages. The Chinese language uses the `jieba` library for word segmentation.
- Provides a Gradio demo interface showcasing the search functionality and displays the top-1 image for a given query.

## How to Use
1. Clone the repository.
2. Ensure you have the necessary dependencies by installing them from `requirements.txt`.
3. Run the Gradio demo (`gradioDemo.py`) to launch the interface.
4. Upload a PDF, set the desired parameters, input your query, and retrieve the associated image.

## Code Overview

### 1. utils.py
Contains utility functions:

- `get_text_around_image`: Extracts surrounding text (both before and after) an image from the given PDF blocks.
- `get_title_of_image`: Retrieves the title of an image based on the nearest occurrence of the terms '图' or 'figure'.

### 2. pdfImage.py
Core functionalities include:

- `ChineseTokenizer` and `ChineseAnalyzer`: Custom tokenizers to handle Chinese tokenization using the `jieba` library.
- `load_pdf`: Converts a given PDF into images and extracts surrounding text for each image.
- `build_index`: Indexes the extracted text using Whoosh.
- `search`: Allows querying the index and retrieves associated images.
- `return_image`: Returns the image based on the search results.

### 3. gradioDemo.py
Sets up the Gradio interface and binds the functions for the demo.

## Demo Interface
The Gradio demo interface (`gradioDemo.py`) offers an interactive way to test the functionality.

- Upload a PDF file.
- Adjust the parameters as needed:
  - DPI
  - Number of front pages to skip
  - Number of back pages to skip
  - Number of blocks to skip
  - Language (English/Chinese)
- Input your search query.
- Hit "Submit" to get the title and the top-1 image associated with your query.

## Dependencies
Refer to `requirements.txt` for a list of necessary libraries.

## Contributing
Feel free to fork the project and submit pull requests. If you encounter any bugs or have suggestions, please open an issue.

