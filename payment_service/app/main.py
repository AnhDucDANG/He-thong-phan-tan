from fastapi import FastAPI
from app.routes.booking_routes import router as booking_router

app = FastAPI()

app.include_router(booking_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)