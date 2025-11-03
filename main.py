from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Products
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"]
)

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "Welcome to the Demo!"

products = [
    Products(id=1, name="phone", description="samsung phone", price=99, quantity=10),
    Products(id=2, name="laptop", description="hp laptop", price=999, quantity=4)
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()
    
    count = db.query(database_models.Products).count()
    
    if count == 0:
        for product in products:
            db.add(database_models.Products(**product.model_dump()))
        db.commit()
        
init_db()

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Products).all()
    return db_products

@app.get("/products/{id}")
def get_products_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == id).first()
    if db_product:
        return db_product
    return "no product found"

@app.post("/products")
def add_product(product: Products, db: Session = Depends(get_db)):
    db.add(database_models.Products(**product.model_dump()))
    db.commit()
    return product

@app.put("/products")
def update_product(id: int, product: Products, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Updated Successfully"
        
    return "Product not found"

@app.delete("/products")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Deleted Successfully"
        
    return "Product not found"