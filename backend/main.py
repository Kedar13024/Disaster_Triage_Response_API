from fastapi import FastAPI

app = FastAPI()

@app.get("/home")
def home():
    return {"msg" : "Welcome!"}
