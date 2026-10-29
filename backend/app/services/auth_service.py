import logging
from datetime import datetime, timezone
from typing import Optional, Union, Any
from bson import ObjectId
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.database.session import get_db
from app.database.mongodb import get_mongodb, is_mongo_online

logger = logging.getLogger("truthguard.auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def register_user(db: Optional[Session], user_in: UserCreate) -> UserResponse:
    clean_email = user_in.email.strip().lower()
    full_name = (user_in.full_name or user_in.name or clean_email.split("@")[0]).strip()
    mongo_db = get_mongodb()

    # 1. Check if user already exists in MongoDB
    if mongo_db is not None and is_mongo_online():
        try:
            existing_mongo = await mongo_db.users.find_one({"email": clean_email})
            if existing_mongo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email address already exists."
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error checking existing user in MongoDB: {e}")

    # 2. Check if user already exists in SQL database (if active)
    if db:
        try:
            existing_sql = db.query(User).filter(User.email == clean_email).first()
            if existing_sql:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email address already exists."
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error checking existing user in SQL DB: {e}")

    hashed_pwd = get_password_hash(user_in.password)
    now_utc = datetime.now(timezone.utc)

    # 3. Store in MongoDB collection `users`
    mongo_user_id: Optional[str] = None
    if mongo_db is not None and is_mongo_online():
        try:
            user_doc = {
                "name": full_name,
                "email": clean_email,
                "password_hash": hashed_pwd,
                "role": "USER",
                "is_active": True,
                "created_at": now_utc
            }
            res = await mongo_db.users.insert_one(user_doc)
            mongo_user_id = str(res.inserted_id)
            logger.info(f"Registered user in MongoDB Atlas: {clean_email} (ID: {mongo_user_id})")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "e11000" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email address already exists."
                )
            logger.error(f"Failed to insert user into MongoDB: {e}")

    # 4. Mirror to SQL database if available
    sql_user = None
    if db:
        try:
            sql_user = User(
                email=clean_email,
                full_name=full_name,
                hashed_password=hashed_pwd,
                role="USER",
                is_active=True
            )
            db.add(sql_user)
            db.commit()
            db.refresh(sql_user)
            logger.info(f"Mirrored user in SQL DB: {clean_email} (ID: {sql_user.id})")
        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            logger.warning(f"Could not persist user to SQL DB: {e}")

    user_id = mongo_user_id or (str(sql_user.id) if sql_user else "1")
    return UserResponse(
        id=user_id,
        email=clean_email,
        full_name=full_name,
        name=full_name,
        role="USER",
        is_active=True,
        created_at=now_utc
    )

async def authenticate_user(db: Optional[Session], credentials: UserLogin) -> UserResponse:
    clean_email = credentials.email.strip().lower()
    mongo_db = get_mongodb()

    # 1. Authenticate against MongoDB
    if mongo_db is not None and is_mongo_online():
        try:
            user_doc = await mongo_db.users.find_one({"email": clean_email})
            if user_doc:
                pwd_hash = user_doc.get("password_hash") or user_doc.get("hashed_password")
                if not pwd_hash or not verify_password(credentials.password, pwd_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password."
                    )
                return UserResponse(
                    id=str(user_doc["_id"]),
                    email=user_doc["email"],
                    full_name=user_doc.get("name") or user_doc.get("full_name") or clean_email.split("@")[0],
                    name=user_doc.get("name") or user_doc.get("full_name"),
                    role=user_doc.get("role", "USER"),
                    is_active=user_doc.get("is_active", True),
                    created_at=user_doc.get("created_at")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error querying user in MongoDB: {e}")

    # 2. Fallback to SQL database
    if db:
        try:
            sql_user = db.query(User).filter(User.email == clean_email).first()
            if sql_user:
                if not verify_password(credentials.password, sql_user.hashed_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password."
                    )
                return UserResponse(
                    id=sql_user.id,
                    email=sql_user.email,
                    full_name=sql_user.full_name,
                    name=sql_user.full_name,
                    role=sql_user.role,
                    is_active=sql_user.is_active,
                    created_at=sql_user.created_at
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error querying user in SQL DB: {e}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password."
    )

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None

    # Check MongoDB
    mongo_db = get_mongodb()
    if mongo_db is not None and is_mongo_online():
        try:
            query = {}
            if ObjectId.is_valid(user_id):
                query = {"_id": ObjectId(user_id)}
            else:
                query = {"$or": [{"_id": user_id}, {"id": user_id}]}
            
            user_doc = await mongo_db.users.find_one(query)
            if user_doc:
                return UserResponse(
                    id=str(user_doc["_id"]),
                    email=user_doc.get("email", ""),
                    full_name=user_doc.get("name") or user_doc.get("full_name"),
                    name=user_doc.get("name") or user_doc.get("full_name"),
                    role=user_doc.get("role", "USER"),
                    is_active=user_doc.get("is_active", True),
                    created_at=user_doc.get("created_at")
                )
        except Exception as e:
            logger.warning(f"Error resolving token from MongoDB: {e}")

    # Fallback to SQL DB
    if db:
        try:
            if str(user_id).isdigit():
                sql_user = db.query(User).filter(User.id == int(user_id)).first()
                if sql_user:
                    return UserResponse(
                        id=sql_user.id,
                        email=sql_user.email,
                        full_name=sql_user.full_name,
                        name=sql_user.full_name,
                        role=sql_user.role,
                        is_active=sql_user.is_active,
                        created_at=sql_user.created_at
                    )
        except Exception as e:
            logger.warning(f"Error resolving token from SQL DB: {e}")

    return None
