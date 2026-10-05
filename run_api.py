import uvicorn

if __name__ == '__main__':
    print('================================================================================')
    print('STARTING ZAWOLF MEDICAL PROCESSING REST API GATEWAY')
    print('================================================================================')
    uvicorn.run('src.api:app', host='0.0.0.0', port=8000, reload=False)
