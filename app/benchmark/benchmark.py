from app.benchmark.accuracyChecker import checkMissingData
from numpy import np
from pandas import pd
import os

def createCSV():
    csv_directory =''


    return csv_directory

def fetchCSV():

    return False

def updateCSV(WER_data, CER_data):

    if WER_data and CER_data: 
        fetchCSV()

        return True
    return False

def getAcccuracy(corrected_data, ocr_data, type):
    data = checkMissingData(corrected_data, ocr_data)
    
    if data:
        return updateCSV(data['average_WER'], data['average_WER'], type)
    return False