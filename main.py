import os
import glob
import sys
from src.pipeline import ProcessingPipeline

sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    pipeline = ProcessingPipeline(ocr_engine='auto')
    test_file = 'data/input/hand_write.jpg'
    
    print(f'Processing {test_file}...')
    res = pipeline.process_file(test_file)
    print('Result status:', res.get('status'))
