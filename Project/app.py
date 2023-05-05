from flask import Flask, url_for, redirect, session, request, render_template
from db_config import mydb, cursor
from PIL import Image
import io
import base64

app = Flask(__name__)
app.secret_key = "Dungdz1st"

@app.route('/')
def home():
   cursor.execute("SELECT * FROM books")
   books = cursor.fetchall()
   return render_template('index.html', books = books, len = len(books), base64 = base64)

@app.route('/crud')
def crud():

   title = request.args.get('title')
   if title != None:
      cursor.execute(
         f'SELECT * FROM books WHERE Title LIKE "%{title}%"')
   else:
      cursor.execute('SELECT * FROM books')
   books = cursor.fetchall()
   return render_template('crud.html', books = books, len = len(books), base64 = base64)


# Tạo đường dẫn add book
@app.route('/add', methods = ['POST'])
def add():
   # Lấy các giá trị ở trong form qua phương thức post
   if request.method == 'POST':
      book_id = request.form.get('book_id')
      title = request.form.get('title')
      author = request.form.get('author')
      genre = request.form.get('genre')
      year = request.form.get('year')
      price = request.form.get('price')
      img = request.files.get('img')
      # Xử lý hình ảnh
      img_binary = None
      if img:
         img_file = request.files['img']
         img_data = img_file.read()
         img_pil = Image.open(io.BytesIO(img_data))
         img_buffer = io.BytesIO()
         img_pil.save(img_buffer, format='JPEG')
         img_binary = img_buffer.getvalue()
         img_base64 = base64.b64encode(img_data)

      # Kiểm tra tác giả và thể loại đã tồn tại trong bảng hay chưa
      sql_check_author = f"SELECT * FROM authors WHERE AuthorName = '{author}'"
      cursor.execute(sql_check_author)
      author_result = cursor.fetchone()

      if not author_result:
          # Thêm tác giả mới nếu không tồn tại trong bảng
          sql_add_author = f"INSERT IGNORE INTO authors (AuthorName) VALUES ('{author}')"
          cursor.execute(sql_add_author)
          mydb.commit()

      sql_check_genre = f"SELECT * FROM genres WHERE GenreName = '{genre}'"
      cursor.execute(sql_check_genre)
      genre_result = cursor.fetchone()

      if not genre_result:
          # Thêm thể loại mới nếu không tồn tại trong bảng
          sql_add_genre = f"INSERT IGNORE INTO genres (GenreName) VALUES ('{genre}')"
          cursor.execute(sql_add_genre)
          mydb.commit()

      # Thêm thông tin book vào cơ sở dữ liệu
      sql = f'INSERT INTO books (BookID, Title, AuthorName, GenreName, PublishYear, Price, Image) VALUES (%s, %s, %s, %s, %s, %s, %s)'
      val = (book_id, title, author, genre, year, price, img_binary)
      cursor.execute(sql, val)
      mydb.commit()

   # Trả về đường dẫn crud
   return redirect('/crud')


@app.route('/update', methods=['GET', 'POST'] )
def update():
   # Lấy các giá trị ở trong form qua phương thức get
   if request.method == 'POST':
      book_id = request.form.get('book_id')
      title = request.form.get('title')
      author = request.form.get('author')
      genre = request.form.get('genre')
      year = request.form.get('year')
      price = request.form.get('price')
      img = request.files.get('img')
      # Xử lý hình ảnh
      img_binary = None
      if img:
         img_file = request.files['img']
         img_data = img_file.read()
         img_pil = Image.open(io.BytesIO(img_data))
         img_buffer = io.BytesIO()
         img_pil.save(img_buffer, format='JPEG')
         img_binary = img_buffer.getvalue()
         img_base64 = base64.b64encode(img_data)
       # Thêm thông tin book vào cơ sở dữ liệu
      sql = 'UPDATE books SET title = %s, AuthorName = %s, GenreName = %s, PublishYear = %s, Price = %s, Image = %s WHERE BookID = %s'
      val = (title, author, genre, year, price, img_binary, book_id)
      cursor.execute(sql, val)
      mydb.commit()
      # trả về đường dẫn crud
   return redirect('/crud')


@app.route('/delete/<book_id>')
def delete(book_id):
   sql = f'DELETE FROM books WHERE BookID = {book_id}'
   cursor.execute(sql)
   mydb.commit()
   return redirect('/crud')


@app.route('/author')
def author():
   name = request.args.get('name')
   if name != None:
      cursor.execute(
         f'SELECT * FROM authors WHERE NameAuthor LIKE "%{name}%"')
   else:
      cursor.execute('SELECT * FROM authors')
   authors = cursor.fetchall()
   return render_template('author.html', authors = authors, len = len(authors))
   

if __name__ == '__main__':
    app.run(debug=True)