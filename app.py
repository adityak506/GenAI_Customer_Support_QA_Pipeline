import os
import uuid
import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

from src.pipeline.inference import run_full_pipeline

from fastapi.middleware.cors import CORSMiddleware
os.makedirs("data", exist_ok=True)  # Ensure the data directory exists for file uploads

# FastAPI: A modern, fast (high-performance) web framework for building APIs with Python, 
# enabling quick development of robust API endpoints for machine learning models.

#FastAPI app instance creation, which serves as the main entry point for defining routes,
# handling requests, and managing the application's lifecycle.
app = FastAPI(
    title="Customer Support QA Evaluator",
    version="1.0"
)

#cross origin resource sharing (CORS) is a security feature implemented in web browsers to prevent 
# malicious websites from making requests to a different domain than the one that served the web page.
#CORSMiddleware is a middle ware (software) that allows which website or application is allowed to 
# communicate with our FastAPI application. In this case, we are allowing all origins, credentials,
# methods, and headers to access our API.   
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# decorators Python syntax (e.g., @app.get("/")) used in FastAPI to associate functions with
# specific HTTP methods and URL paths, effectively turning a Python function into an API endpoint.
@app.get("/health")
def health_check():
    return {"message": "QA Evaluator API is running."}

#UploadFile and File are classes from FastAPI we imported upwards
# that facilitate file uploads in API endpoints.
#We imported them to handle file uploads in our API, allowing users to send files 
# (like CSVs) to the server for processing.
#async will allow the function to run asynchronously, enabling the server to handle multiple requests
# concurrently without blocking. Two users can use the API at the same time without waiting for each other.

@app.post("/evaluate-file")
async def evaluate_file(file: UploadFile = File(...)):
    
    allowed_extensions = [".csv", ".xlsx"]
    file_extension = os.path.splitext(file.filename)[1].lower() #getting extension of the file uploaded by user
    #os.path.splitext(file.filename) -> report.txt -> ["report", ".txt"]
    
    if file_extension not in allowed_extensions:
        return {"error": "Please upload a csv or xlsx file"}
    
    # Create temporary paths
    input_path = f"data/{uuid.uuid4()}{file_extension}"
    output_path = f"data/output_{uuid.uuid4()}.xlsx"
    
    #wb here is write binary mode, which is used to write binary data to a file.
    #await file.read() reads the entire content of the uploaded file asynchronously, allowing the server
    # to handle other tasks while waiting for the file data to be read. The program will not stuck here.
    #this function will allow to save the uploaded file to a temporary location on the server
    # for further processing and then write the content of the uploaded file to that location.
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    if file_extension == ".csv":
        df = pd.read_csv(input_path)
    elif file_extension == ".xlsx":
        df = pd.read_excel(input_path)
        
    output_df = run_full_pipeline(df) #df is the dataframe we got from the uploaded file
    output_df.to_excel(output_path, index=False)
    ##index=False means we don't want to write the index column (like 0, 1 in begining) to the Excel file.
    
    return FileResponse(
        path = output_path,
        filename = "qa_output.xlsx",
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    #FileResponse is a FastAPI response class that allows you to send files as responses to API requests.
    #to get the downloaded file in the browser, the user will get a file named "qa_output.xlsx"
    # with the appropriate media type for Excel files.