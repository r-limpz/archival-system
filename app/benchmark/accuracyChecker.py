import numpy as np
import jiwer

def benchmarkerTest(corrected_data, ocr_data):
    try:
        error_rate = []
        wer_percentile = []
        cer_percentile = []
        mer_percentile = []

        for corrected_item in corrected_data:
            found_in_ocr = False
            empty_text = False
            for ocr_item in ocr_data:
                if int(corrected_item['id']) == int(ocr_item['id']):
                    found_in_ocr = True
    
                    temp_corrected = corrected_item['student_name'].strip()
                    temp_ocr = ocr_item['student_name'].strip()

                    if not temp_corrected == '':
                        output = jiwer.process_words(temp_corrected, temp_ocr)
                        outputChar = jiwer.process_characters(temp_corrected, temp_ocr) 

                        wer_percentile.append(min(output.wer * 100, 100.0))
                        cer_percentile.append(min(outputChar.cer * 100, 100.0))
                        mer_percentile.append(min(output.mer * 100, 100.0))

                        error_rate.append({
                            'id': corrected_item['id'],
                            'wer': min(output.wer * 100, 100.0),
                            'cer': min(outputChar.cer * 100, 100.0),
                            'mer': min(output.mer * 100, 100.0),
                        })
                    else:
                        empty_text = True
                    break
            
            if not found_in_ocr or empty_text:
                wer_percentile.append(100.00)
                cer_percentile.append(100.00)
                mer_percentile.append(100.00)
                error_rate.append({
                    'id': corrected_item['id'],
                    'wer': 100.00,
                    'cer': 100.00,
                    'mer': 100.00
                })
            
        average_WER = np.mean(wer_percentile) if wer_percentile else 0.0
        average_CER = np.mean(cer_percentile) if cer_percentile else 0.0
        average_MER = np.mean(mer_percentile) if mer_percentile else 0.0

        return {
            "error_rate": error_rate,
            "average_WER": average_WER,
            "average_CER": average_CER,
            "average_MER": average_MER
        }
                    
    except Exception as e:
        print(f"benchmarker Error: {e}")
