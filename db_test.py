from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. DB 연결 설정
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/aichat"

# 2. 엔진 및 세션 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. 테스트용 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)

# 4. 테이블 생성 및 연결 테스트
def test_connection():
    try:
        # Base.metadata.create_all 이 맞는 표현입니다!
        Base.metadata.create_all(bind=engine)
        print("✅ MySQL 연결 및 테이블 생성 성공!")
        
        # 데이터 입력 테스트
        db = SessionLocal()
        # 이미 데이터가 있을 경우 에러 방지를 위해 간단한 예외 처리
        test_user = User(username="kyungmin_dev_test")
        db.add(test_user)
        db.commit()
        print("✅ 데이터 입력 성공!")
        db.close()
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()