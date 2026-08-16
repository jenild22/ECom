from sqlmodel import SQLModel, Session, create_engine
from models import Product, User, Order

engine = create_engine("mysql+pymysql://root:Jenil12345@localhost:3306/ecom")

SQLModel.metadata.create_all(engine)

def create_user(user_item: User):
    with Session(engine) as session:
        session.add(user_item)
        session.commit()
        session.refresh(user_item)
        return user_item

def update_user_db(user_id: int, updated_user: User):
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            return None
        
        db_user.username = updated_user.username
        db_user.email = updated_user.email
        db_user.mobile = updated_user.mobile
        db_user.address = updated_user.address
        db_user.password = updated_user.password
        db_user.role = updated_user.role

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

def create_product(product_item: Product):
    with Session(engine) as session:
        session.add(product_item)
        session.commit()
        session.refresh(product_item)
        return product_item