from api.database.database import Base, engine

# Import models so SQLAlchemy registers them

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")