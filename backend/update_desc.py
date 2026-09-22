import sqlite3

conn = sqlite3.connect('../librarypro.db')

conn.row_factory = sqlite3.Row

cur = conn.cursor()

cur.execute('SELECT id, title, author, category FROM books WHERE description LIKE \'%fascinating%\' OR description = \'\' OR description IS NULL')

books = cur.fetchall()

templates = {

    'Science Fiction': "A thrilling exploration of futuristic concepts and advanced technologies in '{title}' by {author}.",

    'Fantasy': "An epic journey through magical realms and mythical creatures awaits in this masterpiece by {author}.",

    'History': "A deep dive into the fascinating historical events that shaped our world.",

    'Computer Science': "A comprehensive guide to fundamental computing concepts and programming paradigms.",

    'Business': "Essential strategies and actionable insights for modern business success by {author}.",

    'Psychology': "An insightful look into human behavior, cognition, and the inner workings of the mind.",

    'Mathematics': "A rigorous and accessible exploration of mathematical principles and applications.",

    'Physics': "Uncovering the fundamental laws of the universe, from quantum mechanics to astrophysics.",

    'Art': "A beautiful and inspiring examination of artistic expression and creative techniques.",

    'Music': "A captivating exploration of musical theory, history, and sonic innovation.",

    'Poetry': "A moving collection of verses that touch the soul and provoke deep reflection.",

    'Biography': "The compelling true story of a remarkable life and lasting legacy.",

    'Romance': "A heartwarming and emotional journey of love, connection, and human relationships.",

    'Mystery': "A gripping and suspenseful puzzle that will keep you guessing until the very end.",

    'Thriller': "A high-stakes, pulse-pounding adventure full of unexpected twists by {author}.",

    'Self-Help': "Practical advice and transformative strategies for personal growth and success.",

    'Classic Fiction': "A timeless literary masterpiece that continues to resonate across generations.",

    'Young Adult': "An engaging and relatable story of coming-of-age, friendship, and self-discovery.",

    'Science': "A fascinating exploration of natural phenomena and scientific discovery.",

    'Finance': "Crucial insights into personal wealth, economic principles, and financial markets."

}

default_template = "An engaging and insightful book by {author}."

for b in books:

    b_id = b['id']

    title = b['title']

    author = b['author']

    category = b['category']

    template = templates.get(category, default_template)

    desc = template.format(title=title, author=author)

    cur.execute('UPDATE books SET description = ? WHERE id = ?', (desc, b_id))

conn.commit()

print(f'Updated {len(books)} books.')

conn.close()

