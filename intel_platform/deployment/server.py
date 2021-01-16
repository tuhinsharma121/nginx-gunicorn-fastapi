from datetime import datetime, timedelta

import jwt
import uvicorn
from fastapi import Depends, HTTPException, status
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from config import *
from intel_platform.deployment.server_models import *
from intel_platform.src.agents.container import ContainerAgent
from intel_platform.src.agents.user import UserAgent
from utils.data_store.rds_data_store import RDSDataStore
from utils.logger.pylogger import get_logger

logger = get_logger("server", "INFO")

tags_metadata = [
    {
        "name": "User",
        "description": "User related endpoints.",
    },
    {
        "name": "Container",
        "description": "Container related endpoints.",
    }

]

app = FastAPI(title=APP_NAME,
              description="Apis for {app_name}".format(app_name=APP_NAME), docs_url="/hxdocs", redoc_url=None,
              version="1.0.0", openapi_tags=tags_metadata, openapi_url="/api/v1/schemas/openapi.json")

app.rds_data_store = None

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.rds_data_store = RDSDataStore(host=PG_HOST, port=PG_PORT,
                                  dbname=PG_DBNAME,
                                  user=PG_USER,
                                  password=PG_PASSWORD)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/schemas/user/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(data_store, user_id: str):
    user_details = UserAgent.get_user_details_for_user_id(data_store=data_store, user_id=user_id)
    if user_details is not None:
        return RegisteredUser(**user_details)


def authenticate_user(data_store, user_id: str, password: str):
    user = get_user(data_store, user_id)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def _get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = get_user(app.rds_data_store, user_id=user_id)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


async def get_current_active_user(current_user: BaseUser = Depends(_get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


@app.get("/", response_model=dict)
async def home_page():
    import time
    t = time.time()
    response = dict()
    response["message"] = app.description
    response["status"] = status.HTTP_200_OK
    logger.info("prod info message")
    logger.info(time.time() - t)
    return response


@app.post("/api/v1/schemas/user/sign-up", response_model=ResponseMessage, tags=["User"],
          summary="Sign up a new user")
async def sign_up_new_user(new_user: NewUser):
    """
        Sign up a new user:
        - **user_id**: the e-mail id of the new user
        - **full_name**: full name of the new user
        - **company_name**: company name of the new user
        - **disabled**: *true* if the new user should be disabled else *false*
        - **password**: password used for signing up by the new user
    """

    user = get_user(app.rds_data_store, user_id=new_user.user_id)
    response = ResponseMessage()
    response.message = "User_id {user_id} is already registered.".format(
        user_id=new_user.user_id)
    response.status = status.HTTP_409_CONFLICT
    if user is None:
        hashed_password = get_password_hash(new_user.password)
        UserAgent.add_new_user(data_store=app.rds_data_store, user_id=new_user.user_id,
                               full_name=new_user.full_name,
                               company_name=new_user.company_name, hashed_password=hashed_password,
                               disabled=new_user.disabled)
        response.message = "Sign up for new user with user_id {user_id} is successful.".format(
            user_id=new_user.user_id)
        response.status = status.HTTP_200_OK

    return response


@app.post("/api/v1/schemas/user/token", response_model=Token, tags=["User"], summary="Login and get access token")
async def login_and_get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
        The user logs in and get an access token for the session:
        - **username**: the e-mail id of the user used as user_id while signing up
        - **password**: password used for signing up by the user
    """

    user = authenticate_user(app.rds_data_store, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/schemas/user/details", response_model=BaseUser, tags=["User"],
         summary="Get details of a logged in user")
async def get_user_details(*, current_user: RegisteredUser = Depends(get_current_active_user)):
    """
        Get details of a logged in user:
        - **access_token**: access token issued by the server to the logged in user
    """
    user = BaseUser(user_id=current_user.user_id, full_name=current_user.full_name,
                    company_name=current_user.company_name, disabled=current_user.disabled)
    return user


@app.get("/api/v1/schemas/container/get-id", response_model=Container, tags=["Container"],
         summary="Get the container id")
async def get_unsecure_container_id(*, name: str, company: str):
    """
        Get the container id which is serving the request:
        - **name**: name of the user
        - **company**: company of the user
    """
    response = Container()
    response.container_id = ContainerAgent.get_contaner_id()
    response.message = "{name} from {company}".format(name=name, company=company)
    return response


@app.post("/api/v1/schemas/container/post-id", response_model=Container, tags=["Container"],
          summary="Get the container id")
async def get_secure_container_id(*, message: Request,
                                  current_user: RegisteredUser = Depends(get_current_active_user)):
    """
        Get the container id which is serving the request:
        - **access_token**: access token issued by the server to the logged in user
        - **name**: name of the user
        - **company**: company of the user
    """
    response = Container()
    response.container_id = ContainerAgent.get_contaner_id()
    response.message = "{name} from {company}".format(name=message.name, company=message.company)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9009)
