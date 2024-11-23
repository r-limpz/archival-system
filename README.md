# OCR-based Table Detection and Text Extraction System (Web Application)

## Overview
This system is a web-based application designed to automate the archival process by converting scanned document images into structured digital text. It leverages Optical Character Recognition (OCR) and table detection algorithms to extract data, which can be stored in a database. The application is specifically targeted for academic settings, such as universities or colleges, to assist registrars in managing student data.

## Tools and Technologies Used

1. **Flask**: A lightweight Python web framework used to build the web application.
2. **DataTables (jQuery)**: Used to display the extracted tabular data in an interactive table format, allowing users to sort, search, and paginate the results.
3. **Table Detection**:
   - The system uses [YOLO Table Detection Model](https://huggingface.co/foduucom/table-detection-and-extraction) to detect and extract tables from scanned documents.
4. **Text Recognition**: 
   - [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) is integrated to recognize and extract text from scanned documents.

## Features

- **Web Interface**: Upload scanned images through the Flask web interface.
- **Table Detection**: Extracts tables from the document using YOLO.
- **Text Recognition**: Extracts textual data from images using PaddleOCR.
- **Data Filtering**: Cleans and processes extracted text for better accuracy.
- **Interactive Data Table**: Displays the extracted data in an interactive table using DataTables and jQuery.

## Purpose
This system is designed for academic settings where the registrar needs to process and store student data. It simplifies the process of digitizing scanned records, transforming them into structured data for easy management, archival, and retrieval.

## Installation

1. Clone the repository:
git clone https://github.com/xrlimpz/archival-system.git

2. Install dependencies:
- You will need Python 3.x and the required libraries listed in the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```

3. Set up PaddleOCR and YOLO models:
- Follow the instructions on their respective repositories for installation and model setup:
  - [PaddleOCR installation guide]([https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/main/README_en.md))
  - [YOLO Table Detection setup](https://huggingface.co/foduucom/table-detection-and-extraction)

4. Ensure that your `serve.py` script is ready to run the Flask server.

## Running the Web Server

1. **Start the Flask server**:
To run the Flask application, execute the `serve.py` script:
```bash
python serve.py
```

2. **Access the Web Application**:
After the server is running, you can access the web application by navigating to:
```bash
127.0.0.1/8080
```

## Acknowledgments
[YOLO Table Detection Model](https://huggingface.co/foduucom/table-detection-and-extraction)
[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR?tab=readme-ov-file)
[DataTables jQuery](https://datatables.net/)
