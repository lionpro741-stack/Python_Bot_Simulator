from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# SQLite база в файле bot.db
engine = create_engine("sqlite:///my_bot/bot.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer,primary_key=True)
    username = Column(String,nullable=True)
    first_name = Column(String,nullable=True)
    money = Column(Integer,default=1000)
    inventory = Column(Integer,default=0)
    profit = Column(Integer,default=0)
    selected_business = Column(String,nullable=True)
    max_items = Column(Integer,default=100)

    def __repr__(self):
        return f"<User {self.user_id} money={self.money}>"

class Business(Base):
    __tablename__ = "business"
    name = Column(String,primary_key=True)
    product = Column(String)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
    emoji = Column(String)

    def __repr__(self):
        return f"<Business {self.name} buy={self.buy_price} sell={self.sell_price}>"


def init_db():
    """Создать таблицы + заполнить бизнесы, если пусто."""
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        if session.query(Business).count() == 0:
            defaults = [
                Business(name="Кафе", product="кофе", buy_price=50, sell_price=70, emoji="☕"),
                Business(name="Магазин одежды", product="рубашка", buy_price=250, sell_price=350, emoji="👗"),
                Business(name="Интернет магазин", product="наушники", buy_price=500, sell_price=600, emoji="🎧"),
                Business(name="Автомойка", product="мойка", buy_price=100, sell_price=150, emoji="🚗"),
            ]
            session.add_all(defaults)
            session.commit()
            print("✅ Бизнесы добавлены в БД")
        else:
            print("ℹ️ Бизнесы уже есть в БД")
    finally:
        session.close()

if __name__ == '__main__':
    init_db()
    print("Создано")






