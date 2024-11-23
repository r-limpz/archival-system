# **Archival Record Digitization System (ARDS)**  
**OCR-based Table Detection and Text Extraction Web Application**

## **Overview**
The Archival Record Digitization System (ARDS) is a web-based application that streamlines the process of converting scanned document images into structured digital data. Using advanced Optical Character Recognition (OCR) and table detection algorithms, the system efficiently extracts and organizes data into a database. It is tailored for academic institutions, such as universities and colleges, to assist registrars in managing student records with greater accuracy and efficiency.

## **Key Features**
- **Web Interface**: Upload scanned images via a user-friendly Flask-based web interface.
- **Advanced Table Detection**: Automatically detects and extracts tables from scanned documents using YOLO.
- **Accurate Text Recognition**: Extracts text from images with high precision using PaddleOCR.
- **Data Cleaning & Filtering**: Processes extracted data to ensure accuracy and readability.
- **Interactive Data Table**: Displays extracted data in a sortable, searchable, and paginated format using DataTables (jQuery).

## **Tools and Technologies**
1. **Flask**: Lightweight Python framework for building the web application.
2. **DataTables (jQuery)**: Provides an interactive tabular view of extracted data, enabling sorting, searching, and pagination.
3. **YOLO Table Detection**:  
   - Utilizes the [YOLO Table Detection Model](https://huggingface.co/foduucom/table-detection-and-extraction) for detecting tables in scanned documents.
4. **PaddleOCR**:  
   - Integrates [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for text recognition and extraction.

## **Purpose**
ARDS addresses the challenges of digitizing archival records in academic settings. By automating the process, it reduces manual effort, improves data accuracy, and ensures that student records are systematically archived and easily retrievable.

---

## **Installation Guide**

### **1. Clone the Repository**
```bash
git clone https://github.com/xrlimpz/archival-system.git
```

### **2. Install Dependencies**
Ensure you have Python 3.x installed, then install the required libraries using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### **3. Set Up PaddleOCR and YOLO Models**
Follow the setup guides from their official repositories:
- [PaddleOCR Installation Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/main/README_en.md)
- [YOLO Table Detection Setup](https://huggingface.co/foduucom/table-detection-and-extraction)

### **4. Verify Application Setup**
Ensure the `serve.py` script is correctly configured to run the Flask application.

---

## **Running the Web Application**

1. **Start the Flask Server**  
   Execute the `serve.py` script to start the server:
   ```bash
   python serve.py
   ```

2. **Access the Application**  
   Once the server is running, open your browser and navigate to:
   ```text
   http://127.0.0.1:8080
   ```

---

## **Acknowledgments**
This system leverages the following technologies and tools:  
- [YOLO Table Detection Model](https://huggingface.co/foduucom/table-detection-and-extraction)  
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)  
- [DataTables jQuery](https://datatables.net/)  

---

### **License**
This project is open-source and available under the [MIT License](LICENSE).

---
