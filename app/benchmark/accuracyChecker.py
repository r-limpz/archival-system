import numpy as np
import jiwer

def wer_checker(final, ocr_result):
    # Define a Compose object for preprocessing
    preprocess = jiwer.Compose([
        jiwer.RemoveEmptyStrings(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
        jiwer.ReduceToListOfListOfWords()
    ])

    # Apply preprocessing to final and ocr_result
    final_processed = preprocess(final)
    ocr_result_processed = preprocess(ocr_result)

    # Calculate Word Error Rate (WER)
    wer = jiwer.wer(final_processed, ocr_result_processed)
    return wer

def cer_checker(final, ocr_result):
    # Define a Compose object for preprocessing
    preprocess = jiwer.Compose([
        jiwer.RemoveEmptyStrings(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip()
    ])

    # Apply preprocessing to final and ocr_result
    final_processed = preprocess(final)
    ocr_result_processed = preprocess(ocr_result)

    # Calculate Character Error Rate (CER)
    cer = jiwer.cer(final_processed, ocr_result_processed)
    return cer

def checkMissingData(corrected_data, ocr_data):
    corrected_ids = {item[0] for item in corrected_data}
    ocr_ids = {item[0] for item in ocr_data}
    
    missing_in_corrected = ocr_ids - corrected_ids 
    missing_in_ocr = corrected_ids - ocr_ids
    
    unique_corrected = []
    unique_ocr = []
    wer_percentile = []
    cer_percentile = []
    
    for item in corrected_data:
        if item[0] in missing_in_corrected:
            unique_corrected.append(item[1])
    
    for item in ocr_data:
        if item[0] in missing_in_ocr:
            unique_ocr.append(item[1])

    #benchmark the accuracy
    if unique_corrected and unique_ocr:
        for corrected_item in unique_corrected:
            max_wer = float('-inf')
            max_cer = float('-inf')
            for ocr_item in unique_ocr:
                currentWER = wer_checker(corrected_item[1], ocr_item[1])
                currentCER = cer_checker(corrected_item[1], ocr_item[1])

            if max_wer < currentWER:
                max_wer = currentWER
            if max_cer < currentCER:
                max_cer = currentCER

            wer_percentile.append(max_wer)
            cer_percentile.append(max_cer)

        return wer_percentile, cer_percentile
    return None

def benhmarker(corrected_data, ocr_data):
    if corrected_data and len(corrected_data) > 0:
        wer_percentile = []
        cer_percentile = []

        #benchmark the accuracy
        for corrected_item in corrected_data:
            for ocr_item in ocr_data:
                if corrected_item[0] == ocr_item[0]:  # Assuming index 0 is the ID
                    wer_percentile.append(wer_checker(corrected_item[1], ocr_item[1]))
                    cer_percentile.append(cer_checker(corrected_item[1], ocr_item[1]))
        
        missingWER, missingCER= checkMissingData(corrected_data, ocr_data)
        wer_percentile.extend(missingWER)
        cer_percentile.extend(missingCER)

        # Calculate average WER and CER using numpy
        if wer_percentile:
            average_WER = np.mean(wer_percentile)
        else:
            average_WER = 0.0  # Handle case where no WER values were appended
        
        if cer_percentile:
            average_CER = np.mean(cer_percentile)
        else:
            average_CER = 0.0  # Handle case where no CER values were appended
        
        return {"average_WER": average_WER, "average_WER":average_CER}
                
    return None 