from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from auth import verify_token

security = HTTPBearer()

def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    # FIX: Remove "Bearer " if present
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    print("CLEAN TOKEN:", token)

    try:
        payload = verify_token(token)
        print("PAYLOAD:", payload)
        return payload
    except Exception as e:
        print("TOKEN ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
    

