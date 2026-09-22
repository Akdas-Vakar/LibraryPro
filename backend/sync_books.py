import os

import sys

import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_utils import get_embedding

from db_helper import get_db

try:

    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

except Exception:

    pass

def sync_embeddings():

    try:

        conn = get_db()

    except Exception as e:

        print(f"[Sync] Error: Could not connect to database: {e}")

        return

    cur = conn.cursor(dictionary=True)

    try:

        cur.execute("SELECT id, title, author, category, description, embedding FROM books")

        books = cur.fetchall()

    except Exception as e:

        print(f"[Sync] Error querying books: {e}")

        cur.close()

        conn.close()

        return

    updated_count = 0

    skipped_count = 0

    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:

        print("[Sync] Warning: No GEMINI_API_KEY found in .env. Skipping embedding generation.")

        print("       (Heuristic fallback searches will be used in-app instead).")

        cur.close()

        conn.close()

        return

    print(f"[Sync] Starting embedding generation for {len(books)} books...")

    for b in books:

        if b['embedding']:

            skipped_count += 1

            continue

        desc = b['description'] if b['description'] else ""

        text = f"{b['title']} by {b['author']}. Category: {b['category']}. {desc}"

        emb = get_embedding(text)

        if emb:

            try:

                cur.execute("UPDATE books SET embedding = %s WHERE id = %s", (json.dumps(emb), b['id']))

                conn.commit()

                updated_count += 1

                print(f"  [OK] Embedded: #{b['id']} - {b['title']}")

            except Exception as e:

                print(f"  [ERROR] Database write failed for #{b['id']}: {e}")

        else:

            print(f"  [ERROR] Failed to get embedding for: #{b['id']} - {b['title']}")

    cur.close()

    conn.close()

    print(f"[Sync] Sync complete! Generated: {updated_count}, Skipped: {skipped_count}")

if __name__ == '__main__':

    sync_embeddings()

