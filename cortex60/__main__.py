import uvicorn

if __name__ == "__main__":
    uvicorn.run("cortex60.app:app", host="127.0.0.1", port=8060, reload=False)
