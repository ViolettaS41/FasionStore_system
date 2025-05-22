from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_user, get_db_connection, get_staff_by_id, update_staff, delete_staff

class User(BaseModel):
    login: str
    password: str
    

class ProductIn(BaseModel):
    name: str
    article: str = Field(..., max_length=10)
    category: str = Field(..., max_length=200)
    parametrs: str
    price: float
    quantity: int

class CategoryIn(BaseModel):
    name: str = Field(..., max_length=200)

class UserUpdate(BaseModel):
    full_name: str
    role: str
    login: str
    post: str


app = FastAPI()

# CORS должен быть первым
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")

# Роутер для API
api_router = APIRouter(prefix="/api", tags=["Products"])

@api_router.get("/products")
async def get_products():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(500, detail="Database connection error")
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT id, name, category, price, quantity
                FROM products
                ORDER BY name
            """)
            return {"products": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        if conn.is_connected():
            conn.close()

@api_router.get("/staff_table")
async def get_staff():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(500, detail="Database connection error")
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT id, full_name, role, login, post
                FROM users
                ORDER BY full_name
            """)
            return {"users": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        if conn.is_connected():
            conn.close()

app.include_router(api_router)

@app.post("/api/add_products")
async def create_product(product: ProductIn):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(500, "Database connection error")
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO products
                    (name, article, category, parametrs, price, quantity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                product.name,
                product.article,
                product.category,
                product.parametrs,
                product.price,
                product.quantity
            ))
            conn.commit()
            return {"status": "ok", "inserted_id": cursor.lastrowid}
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()

@app.post("/api/categories")
async def create_category(cat: CategoryIn):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(500, "Database connection error")
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO category (name) VALUES (%s)"
            cursor.execute(sql, (cat.name,))
            conn.commit()
            return {"status": "ok", "id": cursor.lastrowid}
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()

# Страницы
@app.get('/')
def login_page():
    return FileResponse('login.html')

@app.get('/product')
def product_page():
    return FileResponse('index.html')

@app.get('/staff')
def staff_page():
    return FileResponse('staff.html')

@app.get('/analitic')
def analitic_page():
    return FileResponse('analitic.html')

@app.get('/setting')
def setting_page():
    return FileResponse('settings.html')

@app.get('/add_product')
def add():
    return FileResponse('add_product.html')

# Пользователи
@app.get('/users')
def get_all_users():
    try:
        all_users = get_user()
        return {"users": all_users or [], "count": len(all_users or [])}
    except Exception as e:
        raise HTTPException(500, detail=f"Database error: {e}")

@app.post('/user/id')
def get_user_id(user_data: User):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(500, detail="Database connection error")
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT id FROM users WHERE login = %s AND password_hesh = %s"
            cursor.execute(query, (user_data.login, user_data.password))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, detail="Invalid credentials")
            return {"user_id": result['id']}
    except Exception as e:
        raise HTTPException(500, detail=f"Database error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

@app.put("/api/staff/{staff_id}")
async def update_staff_route(staff_id: int, staff_data: UserUpdate):
    staff = get_staff_by_id(staff_id)  # ✔ Правильный вызов
    if not staff:
        raise HTTPException(status_code=404, detail="Not found")
    
    update_staff(staff_id, staff_data)
    return {"status": "ok"}


@app.delete("/api/staff/{staff_id}")
async def delete_staff(staff_id: int):
    delete_staff(staff_id)
    return {"status": "deleted"}


@app.put("/api/products/{product_id}")
async def update_product(product_id: int, data: ProductIn):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE products
                SET name = %s, category = %s, price = %s, quantity = %s
                WHERE id = %s
            """
            cursor.execute(sql, (data.name, data.category, data.price, data.quantity, product_id))
            conn.commit()
            return {"status": "updated"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            return {"status": "deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"DB error: {e}")
    finally:
        conn.close()
