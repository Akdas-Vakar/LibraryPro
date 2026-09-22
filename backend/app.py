import os

import json

import bcrypt

import urllib.request

from datetime import datetime, date, timedelta

from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

try:

    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

except Exception:

    pass

from ai_utils import get_embedding, cosine_similarity, get_sentiment, get_summary, determine_book_section_ai

from db_helper import get_db

from avl_tree import AVLTree

app = Flask(__name__,

            template_folder='../frontend/templates',

            static_folder='../frontend/static')

app.secret_key = os.environ.get('SECRET_KEY', 'librarypro-secret-2026')

FINE_PER_DAY = 2.00

LOAN_DAYS    = 14

book_avl = AVLTree()

try:

    with app.app_context():

        conn = get_db()

        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM books WHERE isbn IS NOT NULL AND isbn != ''")

        for row in cur.fetchall():

            book_avl.insert(row['isbn'], row)

        cur.close(); conn.close()

        print(f"Loaded {book_avl.size} books into AVL Tree by ISBN.")

except Exception as e:

    print(f"Error loading AVL tree: {e}")

def login_required(f):

    @wraps(f)

    def dec(*a,**k):

        if 'user_id' not in session:

            flash('Please log in first.','warning')

            return redirect(url_for('login'))

        return f(*a,**k)

    return dec

def admin_required(f):

    @wraps(f)

    def dec(*a,**k):

        if 'user_id' not in session: 

            return redirect(url_for('login'))

        if session.get('role') != 'admin':

            flash('Admin access required.','danger')

            return redirect(url_for('dashboard'))

        return f(*a,**k)

    return dec

def get_notifs(uid):

    try:

        c = get_db()

        cur = c.cursor(dictionary=True)

        cur.execute("SELECT * FROM notifications WHERE user_id=%s AND is_read=0 ORDER BY created_at DESC LIMIT 10", (uid,))

        r = cur.fetchall()

        cur.close(); c.close()

        return r

    except:

        return []

def add_notif(uid, msg):

    try:

        c = get_db()

        cur = c.cursor()

        cur.execute("INSERT INTO notifications(user_id,message) VALUES(%s,%s)", (uid, msg))

        c.commit(); cur.close(); c.close()

    except:

        pass

def calc_fine(due):

    if not due or due == '-': 

        return 0.0

    if isinstance(due, str):

        try: 

            due = datetime.strptime(due, '%Y-%m-%d').date()

        except: 

            return 0.0

    d = (date.today() - due).days

    return round(d * FINE_PER_DAY, 2) if d > 0 else 0.0

def get_all_books_sql():

    try:

        conn = get_db()

        cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT 

                b.id, b.title, b.author, b.category, b.total_copies, b.temporarily_off_shelf,

                b.library, b.floor, b.section, b.bookcase, b.shelf, b.slot, b.location_code,

                b.description, b.isbn, b.publication_year, b.publisher, b.cover_url,

                (SELECT COUNT(*) FROM transactions t WHERE t.book_id = b.id AND t.status = 'active') as issued,

                (SELECT COUNT(*) FROM queue q WHERE q.book_id = b.id) as reserved

            FROM books b

            ORDER BY b.title ASC

        """)

        res = cur.fetchall()

        for r in res:

            r['available'] = max(0, r['total_copies'] - r['temporarily_off_shelf'] - r['issued'] - r['reserved'])

        cur.close(); conn.close()

        return res

    except Exception as e:

        print(f"[SQL] Error getting all books: {e}")

        return []

def search_books_sql(query_text):

    if not query_text:

        return get_all_books_sql()

    emb = get_embedding(query_text)

    if emb:

        try:

            conn = get_db()

            cur = conn.cursor(dictionary=True)

            cur.execute("""

                SELECT 

                    b.id, b.title, b.author, b.category, b.total_copies, b.embedding, b.description, b.temporarily_off_shelf,

                    b.library, b.floor, b.section, b.bookcase, b.shelf, b.slot, b.location_code,

                    b.isbn, b.publication_year, b.publisher, b.cover_url,

                    (SELECT COUNT(*) FROM transactions t WHERE t.book_id = b.id AND t.status = 'active') as issued,

                    (SELECT COUNT(*) FROM queue q WHERE q.book_id = b.id) as reserved

                FROM books b

            """)

            books = cur.fetchall()

            cur.close(); conn.close()

            scored_books = []

            for b in books:

                b['available'] = max(0, b['total_copies'] - b['temporarily_off_shelf'] - b['issued'] - b['reserved'])

                score = 0.0

                if b['embedding']:

                    try:

                        book_emb = json.loads(b['embedding'])

                        score = cosine_similarity(emb, book_emb)

                    except:

                        pass

                kw = query_text.lower()

                if kw in b['title'].lower():

                    score += 0.25

                if kw in b['author'].lower():

                    score += 0.15

                if kw in b['category'].lower():

                    score += 0.15

                scored_books.append((score, b))

            scored_books.sort(key=lambda x: x[0], reverse=True)

            results = [b for score, b in scored_books if score > 0.15]

            for r in results:

                if isinstance(r['due_date'], (date, datetime)):

                    r['due_date'] = str(r['due_date'])

                r['fine'] = calc_fine(r['due_date']) if r['issued'] == 1 else 0.0

            return results

        except Exception as e:

            print(f"[SQL] Semantic search failed: {e}. Using fallback...")

    try:

        conn = get_db()

        cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT 

                b.id, b.title, b.author, b.category, b.total_copies, b.temporarily_off_shelf,

                b.library, b.floor, b.section, b.bookcase, b.shelf, b.slot, b.location_code,

                b.description, b.isbn, b.publication_year, b.publisher, b.cover_url,

                (SELECT COUNT(*) FROM transactions t WHERE t.book_id = b.id AND t.status = 'active') as issued,

                (SELECT COUNT(*) FROM queue q WHERE q.book_id = b.id) as reserved

            FROM books b

            WHERE b.title LIKE %s OR b.author LIKE %s OR b.category LIKE %s

            ORDER BY b.title ASC

        """, (f"%{query_text}%", f"%{query_text}%", f"%{query_text}%"))

        res = cur.fetchall()

        for r in res:

            r['available'] = max(0, r['total_copies'] - r['temporarily_off_shelf'] - r['issued'] - r['reserved'])

            r['fine'] = 0.0 

        cur.close(); conn.close()

        return res

    except Exception as e:

        print(f"[SQL] Fallback search error: {e}")

        return []

def get_recommendations_sql(book_id, limit=6):

    try:

        conn = get_db()

        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT id, title, author, category, embedding FROM books WHERE id = %s", (book_id,))

        curr = cur.fetchone()

        if not curr:

            cur.close(); conn.close()

            return []

        cur.execute("""

            SELECT id, title, author, category, embedding, description, isbn, publication_year, publisher, 

                   library, floor, section, bookcase, shelf, slot, cover_url 

            FROM books WHERE id != %s

        """, (book_id,))

        others = cur.fetchall()

        cur.close(); conn.close()

        scored = []

        if curr['embedding']:

            try:

                curr_emb = json.loads(curr['embedding'])

                for b in others:

                    score = 0.0

                    if b['embedding']:

                        try:

                            b_emb = json.loads(b['embedding'])

                            score = cosine_similarity(curr_emb, b_emb)

                        except:

                            pass

                    if b['category'] == curr['category']:

                        score += 0.2

                    if b['author'] == curr['author']:

                        score += 0.2

                    scored.append((score, b))

                scored.sort(key=lambda x: x[0], reverse=True)

                return [item[1] for item in scored[:limit]]

            except Exception as e:

                print(f"[SQL] Vector recommendation error: {e}")

        for b in others:

            score = 0.0

            if b['category'] == curr['category']:

                score += 3.0

            if b['author'] == curr['author']:

                score += 3.0

            w1 = set(curr['title'].lower().split())

            w2 = set(b['title'].lower().split())

            score += len(w1.intersection(w2)) * 0.5

            scored.append((score, b))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [item[1] for item in scored[:limit] if item[0] > 0]

    except Exception as e:

        print(f"[SQL] Fallback recommendation error: {e}")

        return []

def get_stats_sql():

    stats = {'TOTAL': 0, 'ISSUED': 0, 'AVAILABLE': 0}

    try:

        conn = get_db()

        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM books")

        stats['TOTAL'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM transactions WHERE status='active'")

        stats['ISSUED'] = cur.fetchone()[0]

        cur.execute("SELECT SUM(available) FROM books")

        avail = cur.fetchone()[0]

        stats['AVAILABLE'] = avail if avail is not None else 0

        cur.execute("""

            SELECT b.category, COUNT(*) as cnt 

            FROM transactions t 

            JOIN books b ON t.book_id=b.id 

            WHERE t.status='active' 

            GROUP BY b.category

        """)

        for cat, cnt in cur.fetchall():

            stats[f"CAT:{cat}"] = cnt

        cur.close(); conn.close()

    except Exception as e:

        print(f"[SQL] Statistics generation error: {e}")

    return stats

@app.route('/')

def index():

    logged_in = 'user_id' in session

    return render_template('landing.html', logged_in=logged_in)

@app.route('/login', methods=['GET','POST'])

def login():

    if request.method=='POST':

        u = request.form.get('username','').strip()

        p = request.form.get('password','').strip()

        try:

            conn = get_db(); cur = conn.cursor(dictionary=True)

            cur.execute("SELECT * FROM users WHERE username=%s", (u,))

            user = cur.fetchone(); cur.close(); conn.close()

            if user and bcrypt.checkpw(p.encode(), user['password_hash'].encode()):

                for k in ('user_id','username','full_name','role','is_vip'):

                    session[k] = user['id' if k=='user_id' else k]

                flash(f"Welcome back, {user['full_name']}! 👋", 'success')

                return redirect(url_for('dashboard'))

            flash('Invalid username or password.', 'danger')

        except Exception as e:

            flash(f'DB error: {e}', 'danger')

    return render_template('login.html')

@app.route('/logout')

def logout():

    session.clear(); flash('Logged out.', 'info')

    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])

def register():

    if request.method=='POST':

        fn = request.form.get('full_name','').strip()

        un = request.form.get('username','').strip()

        em = request.form.get('email','').strip()

        pw = request.form.get('password','').strip()

        vip = 1 if request.form.get('is_vip') else 0

        ph = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

        try:

            conn = get_db(); cur = conn.cursor()

            cur.execute("INSERT INTO users(username,password_hash,role,full_name,email,is_vip) VALUES(%s,%s,'student',%s,%s,%s)",

                        (un, ph, fn, em, vip))

            conn.commit(); cur.close(); conn.close()

            flash('Account created! Log in.', 'success')

            return redirect(url_for('login'))

        except Exception as e:

            flash(f'Username/email already exists or DB error. {e}', 'danger')

    return render_template('register.html')

@app.route('/dashboard')

@login_required

def dashboard():

    books = get_all_books_sql()

    try:

        conn = get_db(); cur = conn.cursor()

        cur.execute("SELECT SUM(total_copies), SUM(temporarily_off_shelf) FROM books")

        totals = cur.fetchone()

        total = totals[0] if (totals and totals[0] is not None) else 0

        off_shelf = totals[1] if (totals and totals[1] is not None) else 0

        cur.execute("SELECT COUNT(*) FROM transactions WHERE status='active'")

        issued = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM queue")

        qc = cur.fetchone()[0]

        avail = max(0, total - off_shelf - issued - qc)

        cur.close(); conn.close()

    except Exception as e:

        print(f"[SQL] Dashboard stats query failed: {e}")

        total = sum(b['total_copies'] for b in books)

        avail = sum(b.get('available', 0) for b in books)

        issued = sum(b.get('issued', 0) for b in books)

        qc = 0

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT t.*, b.title AS book_title, u.full_name AS student_name

            FROM transactions t 

            JOIN books b ON t.book_id=b.id 

            JOIN users u ON t.user_id=u.id

            ORDER BY t.issue_date DESC LIMIT 5

        """)

        rtx = cur.fetchall(); cur.close(); conn.close()

    except:

        rtx = []

    return render_template('dashboard.html', books=books, total=total, issued=issued,

        available=avail, queue_count=qc, notifications=get_notifs(session['user_id']), recent_tx=rtx)

@app.route('/books')

@login_required

def books():

    q = request.args.get('q','').strip()

    cat = request.args.get('category','').strip()

    loc_lib = request.args.get('loc_lib','').strip()

    loc_floor = request.args.get('loc_floor','').strip()

    loc_sec = request.args.get('loc_sec','').strip()

    loc_bc = request.args.get('loc_bc','').strip()

    loc_sh = request.args.get('loc_sh','').strip()

    loc_sl = request.args.get('loc_sl','').strip()

    sort_by = request.args.get('sort', 'title').strip()

    page = int(request.args.get('page', 1))

    per = int(request.args.get('per', 24))

    all_b = search_books_sql(q)

    if cat:

        all_b = [b for b in all_b if b['category'] == cat]

    if loc_lib:

        all_b = [b for b in all_b if b.get('library') and loc_lib.lower() in b['library'].lower()]

    if loc_floor:

        all_b = [b for b in all_b if b.get('floor') and loc_floor.lower() in b['floor'].lower()]

    if loc_sec:

        all_b = [b for b in all_b if b.get('section') and loc_sec.lower() in b['section'].lower()]

    if loc_bc:

        all_b = [b for b in all_b if b.get('bookcase') and loc_bc.lower() in b['bookcase'].lower()]

    if loc_sh:

        all_b = [b for b in all_b if b.get('shelf') and loc_sh.lower() in b['shelf'].lower()]

    if loc_sl:

        all_b = [b for b in all_b if b.get('slot') and loc_sl.lower() in b['slot'].lower()]

    if sort_by == 'title':

        all_b.sort(key=lambda x: (x.get('title') or '').lower())

    elif sort_by == 'isbn':

        all_b.sort(key=lambda x: x.get('isbn') or '')

    tot = len(all_b)

    tp = max(1, (tot + per - 1) // per)

    page = max(1, min(page, tp))

    paged = all_b[(page - 1) * per:page * per]

    cats = sorted(list(set(b['category'] for b in get_all_books_sql())))

    return render_template('books.html', books=paged, total=tot, page=page, total_pages=tp,

        search=q, cat=cat, sort=sort_by, categories=cats, per=per,

        loc_lib=loc_lib, loc_floor=loc_floor, loc_sec=loc_sec, loc_bc=loc_bc, loc_sh=loc_sh, loc_sl=loc_sl,

        notifications=get_notifs(session['user_id']))

@app.route('/admin_locations', methods=['GET', 'POST'])

@admin_required

def admin_locations():

    if request.method == 'POST':

        action = request.form.get('action')

        try:

            conn = get_db(); cur = conn.cursor()

            if action == 'add_location':

                flash('Location component successfully mapped.', 'success')

            elif action == 'bulk_move':

                q = request.form.get('query', '').strip()

                new_loc = request.form.get('new_location_code', '').strip()

                lib = request.form.get('library', '').strip()

                f = request.form.get('floor', '').strip()

                sec = request.form.get('section', '').strip()

                m = request.form.get('bookcase', '').strip()

                sh = request.form.get('shelf', '').strip()

                sl = request.form.get('slot', '').strip()

                cur.execute("""

                    UPDATE books 

                    SET location_code=%s, library=%s, floor=%s, section=%s, bookcase=%s, shelf=%s, slot=%s 

                    WHERE category=%s OR title LIKE %s

                """, (new_loc, lib, f, sec, m, sh, sl, q, f'%{q}%'))

                conn.commit()

                flash(f'Moved {cur.rowcount} books to {new_loc}.', 'success')

            cur.close(); conn.close()

        except Exception as e:

            flash(f'Error updating locations: {e}', 'danger')

        return redirect(url_for('admin_locations'))

    return render_template('admin_locations.html', notifications=get_notifs(session['user_id']))

@app.route('/api/generate_book_metadata', methods=['POST'])

@login_required

def api_generate_book_metadata():

    data = request.get_json()

    title = data.get('title', '')

    author = data.get('author', '')

    if not title:

        return jsonify({"error": "Title is required for AI generation."}), 400

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:

        return jsonify({"description": f"'{title}' is a notable book authored by {author}."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}

    prompt = f"Write a compelling, professional 2-sentence description for the book '{title}' by {author}."

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=10) as response:

            res = json.loads(response.read().decode('utf-8'))

            text = res['candidates'][0]['content']['parts'][0]['text'].strip()

            return jsonify({"description": text})

    except Exception as e:

        print(f"[AI Description Gen Error] {e}")

        return jsonify({"description": f"'{title}' is a compelling book by {author}."})

@app.route('/api/fetch_isbn', methods=['GET'])

@login_required

def api_fetch_isbn():

    isbn = request.args.get('isbn', '').strip()

    if not isbn:

        return jsonify({"error": "ISBN is required."}), 400

    url = f"https://openlibrary.org/isbn/{isbn}.json"

    req = urllib.request.Request(url, headers={'User-Agent': 'LibraryPro/1.0'})

    try:

        with urllib.request.urlopen(req, timeout=10) as response:

            data = json.loads(response.read().decode('utf-8'))

            title = data.get('title', '')

            pub_year = data.get('publish_date', '')

            if len(pub_year) > 4:

                import re

                match = re.search(r'\d{4}', pub_year)

                pub_year = match.group(0) if match else pub_year

            publishers = data.get('publishers', [])

            publisher = publishers[0] if publishers else ''

            author_names = []

            authors = data.get('authors', [])

            if authors:

                author_key = authors[0].get('key', '')

                if author_key:

                    auth_url = f"https://openlibrary.org{author_key}.json"

                    auth_req = urllib.request.Request(auth_url, headers={'User-Agent': 'LibraryPro/1.0'})

                    try:

                        with urllib.request.urlopen(auth_req, timeout=5) as auth_res:

                            auth_data = json.loads(auth_res.read().decode('utf-8'))

                            author_names.append(auth_data.get('name', ''))

                    except:

                        pass

            author = author_names[0] if author_names else data.get('by_statement', '')

            cover_url = ''

            if data.get('covers'):

                cover_url = f"https://covers.openlibrary.org/b/id/{data['covers'][0]}-L.jpg"

            return jsonify({

                "title": title,

                "author": author,

                "publisher": publisher,

                "publication_year": pub_year,

                "cover_url": cover_url

            })

    except Exception as e:

        print(f"ISBN Fetch Error: {e}")

        return jsonify({"error": str(e)}), 404

@app.route('/add_book', methods=['POST'])

@admin_required

def add_book():

    isbn = request.form.get('isbn','').strip()

    title = request.form.get('title','').strip()

    auth = request.form.get('author','').strip()

    desc = request.form.get('description','').strip()

    pub_year_str = request.form.get('publication_year','').strip()

    publisher = request.form.get('publisher','').strip()

    cover_url = request.form.get('cover_url','').strip()

    total_copies = request.form.get('total_copies', 1)

    try:

        total_copies = int(total_copies)

    except:

        total_copies = 1

    pub_year = None

    if pub_year_str.isdigit():

        pub_year = int(pub_year_str)

    if not all([title, auth]): 

        flash('Title and Author are required.', 'danger')

        return redirect(url_for('books'))

    try:

        ai_loc = determine_book_section_ai(title, auth, '', desc)

        floor = ai_loc.get('floor', 'First Floor')

        section = ai_loc.get('section', 'General Section')

        cat = ai_loc.get('category', 'General')

    except Exception as e:

        print(f"AI loc error: {e}")

        floor = 'First Floor'

        section = 'General Section'

        cat = 'General'

    library = 'Central Library'

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT bookcase, shelf, slot FROM books WHERE section = %s AND floor = %s", (section, floor))

        existing = cur.fetchall()

        b_idx, s_idx, slot_idx = 1, 1, 0

        slots_arr = ['A', 'B', 'C', 'D', 'E']

        if existing:

            max_b, max_s, max_sl = 1, 1, -1

            for r in existing:

                try:

                    b_num = int(r['bookcase'].replace('BC-', '')) if r.get('bookcase') and 'BC-' in r['bookcase'] else 1

                    s_num = int(r['shelf'].replace('S-', '')) if r.get('shelf') and 'S-' in r['shelf'] else 1

                    sl_num = slots_arr.index(r['slot']) if r.get('slot') in slots_arr else 0

                    if b_num > max_b:

                        max_b = b_num; max_s = s_num; max_sl = sl_num

                    elif b_num == max_b and s_num > max_s:

                        max_s = s_num; max_sl = sl_num

                    elif b_num == max_b and s_num == max_s and sl_num > max_sl:

                        max_sl = sl_num

                except Exception as e: pass

            b_idx = max_b

            s_idx = max_s

            slot_idx = max_sl + 1

            if slot_idx >= len(slots_arr):

                slot_idx = 0

                s_idx += 1

                if s_idx > 10:

                    s_idx = 1

                    b_idx += 1

        bookcase = f"BC-{b_idx:02d}"

        shelf = f"S-{s_idx:02d}"

        slot = slots_arr[slot_idx]

        loc_code = f"{library}|{floor}|{section}|{bookcase}|{shelf}|{slot}"

        cur = conn.cursor() 

        cur.execute("""

            INSERT INTO books(title,author,category,description,total_copies,library,floor,section,bookcase,shelf,slot,location_code,available,isbn,publication_year,publisher,cover_url) 

            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """, (title, auth, cat, desc, total_copies, library, floor, section, bookcase, shelf, slot, loc_code, total_copies, isbn, pub_year, publisher, cover_url))

        conn.commit()

        bid = cur.lastrowid

        if isbn:

            new_book_data = {

                'id': bid, 'title': title, 'author': auth, 'category': cat,

                'isbn': isbn, 'publication_year': pub_year, 'publisher': publisher,

                'description': desc, 'location_code': loc_code

            }

            book_avl.insert(isbn, new_book_data)

        text = f"{title} by {auth}. Category: {cat}. {desc}"

        emb = get_embedding(text)

        if emb:

            cur.execute("UPDATE books SET embedding = %s WHERE id = %s", (json.dumps(emb), bid))

            conn.commit()

        cur.close(); conn.close()

        flash(f'Book added! AI allocated it to: {loc_code}. Please place the physical book there.', 'success')

    except Exception as e:

        flash(f'DB error: {e}', 'danger')

    return redirect(url_for('books'))

@app.route('/delete_book', methods=['POST'])

@admin_required

def delete_book():

    bid = request.form.get('book_id','').strip()

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT isbn FROM books WHERE id=%s", (bid,))

        book_to_del = cur.fetchone()

        cur = conn.cursor()

        cur.execute("DELETE FROM books WHERE id=%s", (bid,))

        conn.commit(); cur.close(); conn.close()

        if book_to_del and book_to_del.get('isbn'):

            book_avl.delete(book_to_del['isbn'])

        flash('Book deleted successfully.', 'success')

    except Exception as e:

        flash(f'DB error: {e}', 'danger')

    return redirect(url_for('books'))

@app.route('/api/search_isbn')

def search_isbn():

    isbn = request.args.get('isbn', '').strip()

    if not isbn:

        return jsonify({"error": "ISBN required"}), 400

    book = book_avl.search(isbn)

    if book:

        return jsonify({"status": "found", "book": book})

    return jsonify({"status": "not_found"}), 404

@app.route('/issue', methods=['GET','POST'])

@login_required

def issue_book():

    notifs = get_notifs(session['user_id'])

    if request.method == 'POST':

        isbn = request.form.get('isbn','').strip()

        sn = request.form.get('student_name','').strip()

        si = request.form.get('student_id','').strip()

        vip = 1 if request.form.get('vip') else 0

        idate = date.today()

        ddate = idate + timedelta(days=LOAN_DAYS)

        try:

            conn = get_db()

            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))

            b_row = cur.fetchone()

            if not b_row:

                flash('Book not found with that ISBN.', 'danger')

                cur.close(); conn.close()

                return redirect(url_for('issue_book'))

            bid = b_row['id']

            cur.execute("""

                SELECT b.total_copies, b.temporarily_off_shelf, b.title,

                (SELECT COUNT(*) FROM transactions t WHERE t.book_id = b.id AND t.status = 'active') as issued,

                (SELECT COUNT(*) FROM queue q WHERE q.book_id = b.id) as reserved

                FROM books b WHERE id = %s

            """, (bid,))

            bk = cur.fetchone()

            if not bk:

                flash('Book not found.', 'danger')

                cur.close(); conn.close()

                return redirect(url_for('issue_book'))

            available = max(0, bk['total_copies'] - bk['temporarily_off_shelf'] - bk['issued'] - bk['reserved'])

            cur.execute("SELECT id FROM users WHERE username=%s", (si,))

            ur = cur.fetchone()

            if ur:

                uid = ur['id']

                cur.execute("UPDATE users SET full_name=%s, is_vip=%s WHERE id=%s", (sn, vip, uid))

            else:

                cur.execute("INSERT INTO users(username, password_hash, role, full_name, email, is_vip) VALUES(%s, %s, 'student', %s, %s, %s)", 

                            (si, "", sn, f"{si}@student.com", vip))

                uid = cur.lastrowid

            cur2 = conn.cursor()

            if available > 0:

                cur2.execute("INSERT INTO transactions(book_id,user_id,issue_date,due_date,status) VALUES(%s,%s,%s,%s,'active')",

                             (bid, uid, idate, ddate))

                conn.commit()

                flash(f'👍 Issued! Due: {ddate}', 'success')

            else:

                cur2.execute("INSERT INTO queue(book_id,user_id,priority) VALUES(%s,%s,%s)",

                             (bid, uid, 1 if vip else 2))

                conn.commit()

                flash('📋 Added to waiting queue! VIP priority applied if requested.', 'info')

            cur2.close(); cur.close(); conn.close()

        except Exception as e:

            flash(f'Error issuing book: {e}', 'danger')

        return redirect(url_for('issue_book'))

    books = get_all_books_sql()

    seen = set()

    unique_books = []

    for b in books:

        if b['id'] not in seen:

            seen.add(b['id'])

            unique_books.append(b)

    return render_template('issue.html', books=unique_books, notifications=notifs)

@app.route('/return', methods=['GET','POST'])

@login_required

def return_book():

    notifs = get_notifs(session['user_id'])

    if request.method == 'POST':

        tid = request.form.get('transaction_id','').strip()

        isbn = request.form.get('isbn','').strip()

        rdate = str(date.today())

        try:

            conn = get_db()

            cur = conn.cursor(dictionary=True)

            if tid:

                cur.execute("SELECT * FROM transactions WHERE id=%s AND status='active'", (tid,))

            else:

                cur.execute("SELECT t.* FROM transactions t JOIN books b ON t.book_id = b.id WHERE b.isbn=%s AND t.status='active' ORDER BY t.issue_date ASC LIMIT 1", (isbn,))

            tx = cur.fetchone()

            if tx:

                bid = tx['book_id']

                fine = calc_fine(tx['due_date'])

                cur.execute("SELECT title FROM books WHERE id = %s", (bid,))

                bk_title = cur.fetchone()['title']

                cur2 = conn.cursor()

                cur2.execute("UPDATE transactions SET return_date=%s,status='returned',fine_amount=%s WHERE id=%s",

                             (rdate, fine, tx['id']))

                cur.execute("SELECT * FROM queue WHERE book_id = %s ORDER BY priority ASC, queued_at ASC LIMIT 1", (bid,))

                waiter = cur.fetchone()

                if waiter:

                    cur2.execute("DELETE FROM queue WHERE id = %s", (waiter['id'],))

                    w_ddate = date.today() + timedelta(days=LOAN_DAYS)

                    cur2.execute("INSERT INTO transactions(book_id,user_id,issue_date,due_date,status) VALUES(%s,%s,%s,%s,'active')",

                                 (bid, waiter['user_id'], date.today(), w_ddate))

                    cur2.execute("INSERT INTO notifications(user_id,message) VALUES(%s,%s)",

                                 (waiter['user_id'], f"Waitlist Alert: Book '{bk_title}' is now available! You can now proceed to issue this book."))

                    conn.commit()

                    cur.execute("SELECT full_name FROM users WHERE id = %s", (waiter['user_id'],))

                    w_name = cur.fetchone()['full_name']

                    flash(f"✅ Returned! Auto-assigned to next student on waitlist: {w_name}.", 'success')

                else:

                    conn.commit()

                    flash(f'👍 Book checked in successfully!' + (f' Overdue fine: ₹{fine:.2f}' if fine > 0 else ''),

                          'success' if fine == 0 else 'warning')

                cur2.close()

            else:

                flash('Active checkout record not found for this book.', 'info')

            cur.close(); conn.close()

        except Exception as e:

            flash(f'Error returning book: {e}', 'danger')

        return redirect(url_for('return_book'))

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        if session.get('role') == 'admin':

            cur.execute("""

                SELECT t.id as transaction_id, t.book_id as id, b.isbn as isbn, t.due_date, 

                       b.title, u.full_name as student_name

                FROM transactions t

                JOIN books b ON t.book_id = b.id

                JOIN users u ON t.user_id = u.id

                WHERE t.status = 'active'

            """)

        else:

            cur.execute("""

                SELECT t.id as transaction_id, t.book_id as id, b.isbn as isbn, t.due_date, 

                       b.title, u.full_name as student_name

                FROM transactions t

                JOIN books b ON t.book_id = b.id

                JOIN users u ON t.user_id = u.id

                WHERE t.status = 'active' AND t.user_id = %s

            """, (session['user_id'],))

        active_txs = cur.fetchall()

        cur.close(); conn.close()

        for t in active_txs:

            t['fine'] = calc_fine(t['due_date'])

    except Exception as e:

        print(f"[SQL] Error fetching active transactions for return page: {e}")

        active_txs = []

    return render_template('return.html', books=active_txs, notifications=notifs)

@app.route('/queue')

@login_required

def queue_page():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT q.book_id, b.title as book_title, u.full_name as student, u.username as sid,

                   CASE WHEN q.priority = 1 THEN 'VIP' ELSE 'Regular' END as type

            FROM queue q

            JOIN books b ON q.book_id = b.id

            JOIN users u ON q.user_id = u.id

            ORDER BY q.priority ASC, q.queued_at ASC

        """)

        entries = cur.fetchall()

        cur.close(); conn.close()

    except Exception as e:

        print(f"[SQL] Queue page fetch error: {e}")

        entries = []

    return render_template('queue.html', entries=entries, notifications=get_notifs(session['user_id']))

@app.route('/books/<int:book_id>/queue', methods=['POST'])

@login_required

def join_queue(book_id):

    uid = session['user_id']

    role = session.get('role')

    vip = session.get('is_vip', 0)

    try:

        conn = get_db()

        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT available, title FROM books WHERE id = %s", (book_id,))

        bk = cur.fetchone()

        if not bk:

            flash('Book not found.', 'danger')

            cur.close(); conn.close()

            return redirect(url_for('books'))

        if bk['available'] > 0:

            flash(f"Book '{bk['title']}' is currently available. You can borrow it directly!", 'info')

            cur.close(); conn.close()

            return redirect(url_for('books'))

        cur.execute("SELECT * FROM queue WHERE book_id = %s AND user_id = %s", (book_id, uid))

        exists = cur.fetchone()

        if exists:

            flash(f"You are already in the waiting list for '{bk['title']}'.", 'info')

            cur.close(); conn.close()

            return redirect(url_for('books'))

        cur2 = conn.cursor()

        cur2.execute("INSERT INTO queue(book_id, user_id, priority) VALUES(%s, %s, %s)", 

                     (book_id, uid, 1 if vip else 2))

        conn.commit()

        cur2.close(); cur.close(); conn.close()

        flash(f"📋 Successfully joined the waitlist for '{bk['title']}'!", 'success')

    except Exception as e:

        flash(f"Error joining queue: {e}", 'danger')

    return redirect(url_for('books'))

@app.route('/stack')

@login_required

def stack_page():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT t.book_id, b.title

            FROM transactions t

            JOIN books b ON t.book_id = b.id

            WHERE t.status = 'returned'

            ORDER BY t.return_date DESC, t.id DESC

            LIMIT 20

        """)

        entries = cur.fetchall()

        cur.close(); conn.close()

    except Exception as e:

        print(f"[SQL] Stack page fetch error: {e}")

        entries = []

    return render_template('stack.html', entries=entries, notifications=get_notifs(session['user_id']))

@app.route('/recommend/<int:book_id>')

@login_required

def recommend(book_id):

    recs = get_recommendations_sql(book_id, limit=6)

    return jsonify(recs)

@app.route('/analytics')

@admin_required

def analytics():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT DATE(issue_date) AS day,COUNT(*) AS cnt FROM transactions WHERE issue_date>=DATE_SUB(CURDATE(),INTERVAL 14 DAY) GROUP BY day ORDER BY day")

        di = cur.fetchall()

        cur.execute("SELECT b.title,COUNT(t.id) AS cnt FROM transactions t JOIN books b ON t.book_id=b.id GROUP BY b.title ORDER BY cnt DESC LIMIT 8")

        pop = cur.fetchall()

        cur.execute("SELECT u.full_name,COUNT(t.id) AS cnt FROM transactions t JOIN users u ON t.user_id=u.id WHERE t.status='active' GROUP BY u.full_name ORDER BY cnt DESC LIMIT 8")

        au = cur.fetchall()

        cur.execute("SELECT category,COUNT(*) AS cnt FROM books GROUP BY category ORDER BY cnt DESC")

        cats = cur.fetchall()

        cur.execute("SELECT t.*,b.title,u.full_name,DATEDIFF(CURDATE(),t.due_date) AS days_late FROM transactions t JOIN books b ON t.book_id=b.id JOIN users u ON t.user_id=u.id WHERE t.status='active' AND t.due_date<CURDATE() ORDER BY days_late DESC")

        ov = cur.fetchall(); cur.close(); conn.close()

    except:

        di = pop = au = cats = ov = []

    stats = get_stats_sql()

    return render_template('analytics.html', daily_issues=di, popular=pop, active_users=au,

        categories=cats, overdue=ov, stats=stats, notifications=get_notifs(session['user_id']))

@app.route('/students')

@admin_required

def students():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT u.*, COUNT(t.id) AS total_borrowed,

            SUM(CASE WHEN t.status='active' THEN 1 ELSE 0 END) AS currently_borrowed,

            COALESCE(SUM(t.fine_amount), 0) AS total_fines

            FROM users u 

            LEFT JOIN transactions t ON u.id=t.user_id

            WHERE u.role='student' 

            GROUP BY u.id 

            ORDER BY u.full_name

        """)

        sd = cur.fetchall(); cur.close(); conn.close()

    except Exception as e:

        print(f"[SQL] Students list fetch error: {e}")

        sd = []

    return render_template('students.html', students=sd, notifications=get_notifs(session['user_id']))

@app.route('/transactions')

@admin_required

def transactions():

    page = int(request.args.get('page', 1))

    per = 15

    off = (page - 1) * per

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) AS c FROM transactions")

        tot = cur.fetchone()['c']

        cur.execute("""

            SELECT t.*, b.title AS book_title, u.full_name AS student_name,

            DATEDIFF(CURDATE(),t.due_date) AS days_late

            FROM transactions t 

            JOIN books b ON t.book_id=b.id 

            JOIN users u ON t.user_id=u.id

            ORDER BY t.issue_date DESC LIMIT %s OFFSET %s

        """, (per, off))

        txs = cur.fetchall(); cur.close(); conn.close()

    except:

        txs = []; tot = 0

    tp = max(1, (tot + per - 1) // per) if tot else 1

    return render_template('transactions.html', transactions=txs, page=page, total_pages=tp,

        notifications=get_notifs(session['user_id']))

@app.route('/profile')

@login_required

def profile():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT t.*, b.title AS book_title FROM transactions t JOIN books b ON t.book_id=b.id WHERE t.user_id=%s ORDER BY t.issue_date DESC", (session['user_id'],))

        mb = cur.fetchall(); cur.close(); conn.close()

    except:

        mb = []

    for t in mb:

        if t['status'] == 'active':

            t['fine_amount'] = calc_fine(t['due_date'])

    tf = sum(t['fine_amount'] for t in mb if t['status']=='active')

    return render_template('profile.html', my_books=mb, total_fine=tf, today_date=date.today(), notifications=get_notifs(session['user_id']))

@app.route('/notifications/mark_read', methods=['POST'])

@login_required

def mark_notifications_read():

    try:

        conn = get_db(); cur = conn.cursor()

        cur.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))

        conn.commit(); cur.close(); conn.close()

    except:

        pass

    return jsonify({'status':'ok'})

@app.route('/api/stats')

@login_required

def api_stats():

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT DATE(issue_date) AS day,COUNT(*) AS cnt FROM transactions WHERE issue_date>=DATE_SUB(CURDATE(),INTERVAL 7 DAY) GROUP BY day ORDER BY day")

        daily = cur.fetchall()

        cur.execute("SELECT b.category,COUNT(*) AS cnt FROM transactions t JOIN books b ON t.book_id=b.id GROUP BY b.category")

        cats = cur.fetchall()

        cur.execute("SELECT COUNT(*) AS c FROM transactions WHERE status='active'")

        active = cur.fetchone()['c']

        cur.execute("SELECT COUNT(*) AS c FROM transactions WHERE status='active' AND due_date<CURDATE()")

        ov = cur.fetchone()['c']

        cur.close(); conn.close()

        return jsonify({'daily':[{'day':str(r['day']),'cnt':r['cnt']} for r in daily],

            'cats':[{'cat':r['category'],'cnt':r['cnt']} for r in cats],'active':active,'overdue':ov})

    except Exception as e:

        return jsonify({'error':str(e), 'daily':[], 'cats':[], 'active':0, 'overdue':0})

@app.route('/chatbot')

@login_required

def chatbot():

    return render_template('chatbot.html', notifications=get_notifs(session['user_id']))

@app.route('/api/chat', methods=['POST'])

@login_required

def api_chat():

    data = request.json or {}

    msg = data.get('message', '').strip()

    if not msg:

        return jsonify({'response': "I didn't hear anything. How can I help you today?"})

    api_key = os.environ.get('GEMINI_API_KEY')

    msg_lower = msg.lower()

    if any(kw in msg_lower for kw in ["search for", "find book", "do you have", "show me books", "looking for books"]):

        query_text = ""

        for phrase in ["search for", "find book", "do you have", "show me books", "looking for"]:

            if phrase in msg_lower:

                idx = msg_lower.find(phrase) + len(phrase)

                query_text = msg[idx:].strip('?." \n')

                break

        if query_text:

            results = search_books_sql(query_text)

            if results:

                book_list = "\n".join([f"- **{b['title']}** by {b['author']} ({b['category']}) — {'Available' if b['available']>0 else 'Checked out'} (Location: {b.get('location_code', 'Unassigned')})" for b in results[:5]])

                return jsonify({'response': f"Here are the books I found for '{query_text}':\n\n{book_list}"})

            else:

                return jsonify({'response': f"I couldn't find any books matching '{query_text}' in our library."})

    if any(kw in msg_lower for kw in ["my books", "what did i borrow", "active loans", "my fines", "do i owe", "due date"]):

        try:

            conn = get_db(); cur = conn.cursor(dictionary=True)

            cur.execute("""

                SELECT t.*, b.title FROM transactions t 

                JOIN books b ON t.book_id = b.id 

                WHERE t.user_id = %s AND t.status = 'active'

            """, (session['user_id'],))

            loans = cur.fetchall(); cur.close(); conn.close()

            if loans:

                loan_list = []

                total_fine = 0.0

                for l in loans:

                    fine = calc_fine(l['due_date'])

                    total_fine += fine

                    fine_str = f" (Overdue fine: ₹{fine:.2f})" if fine > 0 else ""

                    loan_list.append(f"- **{l['title']}** (Due: {l['due_date']}){fine_str}")

                loan_text = "\n".join(loan_list)

                response_text = f"You currently have these books checked out:\n\n{loan_text}\n\n"

                if total_fine > 0:

                    response_text += f"⚠️ **Total outstanding fine**: ₹{total_fine:.2f}."

                else:

                    response_text += "✅ You have no outstanding fines."

                return jsonify({'response': response_text})

            else:

                return jsonify({'response': "You don't have any books checked out right now! Everything is clear."})

        except Exception as e:

            return jsonify({'response': f"Error retrieving your records: {e}"})

    if api_key:

        history = data.get('history', [])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent?key={api_key}"

        headers = {'Content-Type': 'application/json'}

        system_prompt = (

            "You are LibraryPro's AI Assistant, a friendly and professional chatbot for a university physical library. "

            "Help the user with library policies, rules (14-day checkout, ₹2.00 fine per day), and general reading queries. "

            "You are also aware of the physical library layout, where books are stored in a specific Floor -> Section -> bookcase -> Shelf -> Slot hierarchy. "

            "Keep your responses concise, clear, and formatted in markdown."

        )

        if history and len(history) > 0:

            if history[0].get('role') == 'user':

                original_text = history[0]['parts'][0]['text']

                if not original_text.startswith("You are LibraryPro's AI Assistant"):

                    history[0]['parts'][0]['text'] = f"{system_prompt}\n\nUser: {original_text}"

        else:

            history = [{"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser: {msg}"}]}]

        payload = {

            "contents": history

        }

        try:

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

            with urllib.request.urlopen(req, timeout=30) as response:

                res = json.loads(response.read().decode('utf-8'))

                ans = res['candidates'][0]['content']['parts'][0]['text'].strip()

                return jsonify({'response': ans})

        except urllib.error.HTTPError as e:

            print(f"[Chatbot API] HTTP Error {e.code}: {e.read().decode('utf-8') if hasattr(e, 'read') else str(e)}")

        except Exception as e:

            print(f"[Chatbot API] Error calling Gemini API: {e}")

    fallback_responses = {

        "hello": "Hello! I am your LibraryPro Assistant. How can I help you manage your books today?",

        "hi": "Hi there! Welcome to the library. Ask me to search for books or check your loan history!",

        "help": "I can help you:\n1. Search the book catalog (e.g. *'search for Python'*)\n2. Check your active checkouts (*'what did I borrow?'*)\n3. Check library hours and fine policy.",

        "hours": "The library is open Monday through Friday from 9:00 AM to 6:00 PM. We are closed on weekends.",

        "rules": "Books can be borrowed for up to 14 days. After that, an overdue fine of ₹2.00 per day will apply.",

        "fine": "Standard overdue fines are ₹2.00 per day. You can view your current outstanding fine by asking *'what did I borrow?'* or visiting your Profile.",

    }

    for k, v in fallback_responses.items():

        if k in msg_lower:

            return jsonify({'response': v})

    if not api_key:

        response = (

            "I'm here as your LibraryPro Assistant! You can ask me to search for books (e.g., *'search for Algorithms'*), "

            "check your borrowings (*'what did I borrow?'*), or inquire about library rules and hours.\n\n"

            "*(Tip: Set a GEMINI_API_KEY in the .env file to unlock full conversational AI capability!)*"

        )

    else:

        response = (

            "The AI service is currently experiencing high demand and is temporarily unavailable. "

            "I can still help you with basic commands like *'search for [book]'* or *'what did I borrow?'*."

        )

    return jsonify({'response': response})

@app.route('/book/<int:book_id>/review', methods=['POST'])

@login_required

def add_review(book_id):

    rating = request.form.get('rating')

    review_text = request.form.get('review_text', '').strip()

    if not rating:

        flash('Please select a rating from 1 to 5 stars.', 'danger')

        return redirect(url_for('books'))

    sentiment = get_sentiment(review_text) if review_text else 'Neutral'

    try:

        conn = get_db(); cur = conn.cursor()

        cur.execute("""

            INSERT INTO reviews (book_id, user_id, rating, review_text, sentiment)

            VALUES (%s, %s, %s, %s, %s)

        """, (book_id, session['user_id'], rating, review_text, sentiment))

        conn.commit(); cur.close(); conn.close()

        flash('Your review has been posted and analyzed successfully!', 'success')

    except Exception as e:

        flash(f'Error submitting review: {e}', 'danger')

    return redirect(url_for('books'))

@app.route('/book/<int:book_id>/reviews')

@login_required

def get_book_reviews(book_id):

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("""

            SELECT r.*, u.full_name as reviewer_name 

            FROM reviews r

            JOIN users u ON r.user_id = u.id

            WHERE r.book_id = %s

            ORDER BY r.created_at DESC

        """, (book_id,))

        revs = cur.fetchall(); cur.close(); conn.close()

        for r in revs:

            if isinstance(r['created_at'], (date, datetime)):

                r['created_at'] = r['created_at'].strftime('%b %d, %Y')

        return jsonify({'status': 'success', 'reviews': revs})

    except Exception as e:

        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/book/<int:book_id>/summary')

@login_required

def get_book_summary(book_id):

    try:

        conn = get_db(); cur = conn.cursor(dictionary=True)

        cur.execute("SELECT title, author, category, description FROM books WHERE id = %s", (book_id,))

        b = cur.fetchone(); cur.close(); conn.close()

        if b:

            summary = get_summary(b['title'], b['author'], b['category'], b['description'])

            return jsonify({'status': 'success', 'summary': summary})

        return jsonify({'status': 'error', 'message': 'Book not found'})

    except Exception as e:

        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/about')

def about():

    return render_template('about.html')

@app.errorhandler(404)

def not_found(e): 

    return render_template('error.html', code=404, msg="Page not found."), 404

@app.errorhandler(500)

def server_error(e): 

    return render_template('error.html', code=500, msg="Server error."), 500

@app.context_processor

def inject_globals():

    nc = 0

    notifs = []

    if 'user_id' in session:

        try:

            conn = get_db(); cur = conn.cursor(dictionary=True)

            cur.execute("SELECT COUNT(*) AS c FROM notifications WHERE user_id=%s AND is_read=0", (session['user_id'],))

            nc = cur.fetchone()['c']

            cur.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 10", (session['user_id'],))

            notifs = cur.fetchall()

            for n in notifs:

                if isinstance(n['created_at'], (date, datetime)):

                    n['created_at_str'] = n['created_at'].strftime('%b %d, %Y %H:%M')

                else:

                    n['created_at_str'] = str(n['created_at'])

            cur.close(); conn.close()

        except: 

            pass

    return {'notif_count': nc, 'notifications': notifs, 'current_year': datetime.now().year}

if __name__=='__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)

