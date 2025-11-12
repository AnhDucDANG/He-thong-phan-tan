from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://sa:Lyly2505@localhost/CarBookingDB?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # pool_pre_ping=True giúp kiểm tra kết nối CSDL còn hoạt động không
    # isolation_level="READ COMMITTED" (mức độ cao hơn cho concurrency)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base class
Base = declarative_base()

# Hàm Utility để lấy DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()