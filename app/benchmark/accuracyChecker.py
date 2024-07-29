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
            for ocr_item in ocr_data:
                if int(corrected_item['id']) == int(ocr_item['id']):
                    found_in_ocr = True
                    temp_corrected = corrected_item['student_name'].strip()
                    temp_ocr = ocr_item['student_name'].strip()

                    output = jiwer.process_words(temp_corrected, temp_ocr)
                    outputChar = jiwer.process_characters(temp_corrected, temp_ocr)

                    wer_percentile.append(output.wer * 100)
                    cer_percentile.append(outputChar.cer * 100)
                    mer_percentile.append(output.mer * 100)

                    error_rate.append({
                        'id': corrected_item['id'],
                        'wer': output.wer * 100,
                        'cer': outputChar.cer * 100,
                        'mer': output.mer * 100,
                    })
                    break
            
            if not found_in_ocr:
                wer_percentile.append(0.0)
                cer_percentile.append(0.0)
                mer_percentile.append(0.0)
                error_rate.append({
                    'id': corrected_item['id'],
                    'wer': 0.0,
                    'cer': 0.0,
                    'mer': 0.0
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
