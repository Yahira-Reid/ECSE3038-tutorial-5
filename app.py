import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.
@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.post("/devices", status_code=201)
def create_device(device: Device, response: Response):
    if devices.find_one({"name": device.name}):
        raise HTTPException(status_code=409, detail="Device already exists: " + device.name)
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    response.headers["Location"] = "/devices/" + device.name
    return new_device

@app.put("/devices/{name}")
def put_device(name: str, device: Device, response: Response):
    if device.name != name:
        raise HTTPException(status_code=409, detail="Name in body must match name in URL")
    new_device = device.model_dump()
    result = devices.replace_one({"name": name}, new_device, upsert=True)
    if result.upserted_id is not None:
        response.status_code = 201
    return new_device
