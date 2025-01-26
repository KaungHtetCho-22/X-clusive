from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Database setup
DATABASE_URL = "sqlite:///app-data/X-clusive.db"  # Use SQLite for simplicity
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for many-to-many relationship between groups and users
group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    expenses = relationship("Expense", back_populates="payer")
    groups = relationship("Group", secondary=group_members, back_populates="members")

# Group model
class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    members = relationship("User", secondary=group_members, back_populates="groups")
    expenses = relationship("Expense", back_populates="group")

# Expense model
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    category = Column(String)
    date = Column(DateTime, default=lambda: datetime.now())
    payer_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    payer = relationship("User", back_populates="expenses")
    group = relationship("Group", back_populates="expenses")

# Create tables
Base.metadata.create_all(bind=engine)

# Database utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()