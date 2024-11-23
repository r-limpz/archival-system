# OCR-based Table Detection and Text Extraction System

## Overview
This system leverages Optical Character Recognition (OCR) and advanced table detection algorithms to streamline the archival process of records. The system is designed to convert scanned image documents into editable digital text, which can then be stored in a database. It is specifically tailored for academic settings where a registrar needs to efficiently manage student data in the data management cycle.

## Tools and Technologies Used

1. **Table Detection**: 
   - The system uses [YOLO Table Detection Model](https://github.com/foduucom/table-detection-and-extraction) to detect and extract tabular data from scanned documents. YOLO (You Only Look Once) is a real-time object detection system that is well-suited for this task.
   
2. **Text Recognition**: 
   - For text recognition, the system integrates [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), a powerful open-source OCR tool that can recognize and extract text from scanned documents with high accuracy.
   
3. **Text Filtering**: 
   - Text filtering algorithms are used to clean and pre-process the recognized text, removing any noise or irrelevant data, ensuring that the output is clean and structured for further use in a database.

## Features

- **Table Detection**: Automatically detects and extracts tables from scanned document images using YOLO.
- **Text Recognition**: Extracts accurate text data from scanned images using PaddleOCR.
- **Data Filtering**: Preprocesses the recognized text to remove unwanted elements and noise.
- **Database Integration**: After extraction and cleaning, the text data can be easily integrated into a database for storage and further processing.
- **Efficient Archival**: Significantly improves the efficiency of converting archival records from physical scanned images to digital format.

## Purpose
This system is specifically designed for use in academic settings, such as universities or colleges, where the registrar's office needs to store and manage large volumes of student data. The goal is to digitize scanned documents and organize the extracted data in a structured format, ready for database storage and retrieval.

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/ocr-table-detection-system.git

2. Install dependencies:
- You may need to install required Python libraries and dependencies:
  ```bash
  pip install -r requirements.txt
  ```

3. Set up PaddleOCR and YOLO models:
- Follow the instructions on their respective repositories for installation and model setup.
  - [PaddleOCR installation guide](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/installation_en.md)
  - [YOLO Table Detection setup](https://github.com/foduucom/table-detection-and-extraction)

4. Run the system:
- After setup, you can run the script to process your scanned documents and extract data:
  ```bash
  python process_document.py --input <path_to_scanned_image> --output <output_text_file>
  ```

## Usage

1. Place the scanned image document (PDF or image file) that needs to be processed in the input folder.
2. Run the processing script, and the system will:
- Detect tables within the document.
- Extract text using OCR.
- Filter and clean the extracted text.
3. The output will be a structured text file or CSV file containing the digitized student data, ready for insertion into a database.

## Example

Here’s a simple example of how the system works:

- **Input**: A scanned image of a student registration form with tables and personal data.
- **Output**: A CSV file containing the structured student information (Name, Date of Birth, Address, etc.).

## Contributing

We welcome contributions to improve this system. If you would like to contribute, please fork the repository, make your changes, and submit a pull request.

### Issues
If you encounter any issues, please open an issue on the GitHub repository, and we will address it as soon as possible.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Acknowledgments
- [YOLO Table Detection Model]([https://github.com/foduucom/table-detection-and-extraction](https://huggingface.co/foduucom/table-detection-and-extraction))
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- Special thanks to the open-source community for their invaluable contributions.

