from typing import Optional, List
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import API.prediciton as prediction
import uvicorn

app = FastAPI()


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    result = prediction.main(files, 15)
    print(result)
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
