import os
import sys
import json


backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')

sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.join(backend_path, 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
except Exception:
    pass

from ai_utils import get_embedding
from db_helper import get_db

books_data = [
    
    {"title": "Effective C++", "author": "Scott Meyers", "category": "Programming", "description": "55 specific ways to improve your programs and designs.", "copies": 3},
    {"title": "JavaScript: The Good Parts", "author": "Douglas Crockford", "category": "Programming", "description": "Unearthing the really good parts of JavaScript.", "copies": 2},
    {"title": "Head First Design Patterns", "author": "Eric Freeman", "category": "Programming", "description": "A brain-friendly guide to software design patterns.", "copies": 4},
    {"title": "Python Cookbook", "author": "David Beazley", "category": "Programming", "description": "Recipes for mastering Python 3 code and programming idioms.", "copies": 3},
    {"title": "The Go Programming Language", "author": "Alan Donovan", "category": "Programming", "description": "The authoritative guide for writing Go programs.", "copies": 2},
    {"title": "Rust Programming", "author": "Steve Klabnik", "category": "Programming", "description": "Official guide to the Rust programming language.", "copies": 3},
    {"title": "C++ Primer", "author": "Stanley Lippman", "category": "Programming", "description": "Comprehensive introduction to the C++ standard library.", "copies": 2},
    {"title": "Programming Pearls", "author": "Jon Bentley", "category": "Programming", "description": "Witty essays on coding, sorting, and algorithm design.", "copies": 2},
    {"title": "Fluent Python", "author": "Luciano Ramalho", "category": "Programming", "description": "Write idiomatic Python code by utilizing its best features.", "copies": 3},
    {"title": "Code Complete", "author": "Steve McConnell", "category": "Programming", "description": "A practical handbook of software construction rules.", "copies": 2},
    {"title": "Java: A Beginner's Guide", "author": "Herbert Schildt", "category": "Programming", "description": "Start programming in Java immediately with this guide.", "copies": 4},
    {"title": "Eloquent JavaScript", "author": "Marijn Haverbeke", "category": "Programming", "description": "A modern introduction to programming and web development.", "copies": 3},

    
    {"title": "The Art of Computer Programming", "author": "Donald Knuth", "category": "Computer Science", "description": "The monumental work on algorithms and data structures.", "copies": 1},
    {"title": "Structure and Interpretation of Computer Programs", "author": "Abelson & Sussman", "category": "Computer Science", "description": "Classic text on functional programming using Scheme.", "copies": 2},
    {"title": "Algorithms", "author": "Robert Sedgewick", "category": "Computer Science", "description": "Surveys the most important computer algorithms in use today.", "copies": 3},
    {"title": "Introduction to the Theory of Computation", "author": "Michael Sipser", "category": "Computer Science", "description": "Standard textbook on formal languages and automata theory.", "copies": 2},
    {"title": "Computer Architecture: A Quantitative Approach", "author": "Hennessy & Patterson", "category": "Computer Science", "description": "The definitive guide to hardware and system architecture.", "copies": 2},
    {"title": "Compilers: Principles, Techniques, and Tools", "author": "Aho, Lam, Sethi, Ullman", "category": "Computer Science", "description": "The dragon book on compiler design and construction.", "copies": 2},
    {"title": "Modern Operating Systems", "author": "Andrew Tanenbaum", "category": "Computer Science", "description": "Clear conceptual explanations of modern operating systems.", "copies": 3},
    {"title": "Algorithms + Data Structures = Programs", "author": "Niklaus Wirth", "category": "Computer Science", "description": "Fundamental textbook on classic computer algorithms.", "copies": 2},
    {"title": "The Mythical Man-Month", "author": "Fred Brooks", "category": "Computer Science", "description": "Essays on software engineering and team management.", "copies": 3},
    {"title": "Pattern Classification", "author": "Richard Duda", "category": "Computer Science", "description": "Classic textbook on pattern recognition and classification.", "copies": 2},
    {"title": "Introduction to Automata Theory", "author": "John Hopcroft", "category": "Computer Science", "description": "Formal languages, automata, and computational complexity.", "copies": 2},
    {"title": "Distributed Systems", "author": "Maarten van Steen", "category": "Computer Science", "description": "Principles and paradigms of distributed software engineering.", "copies": 3},

    
    {"title": "Database System Concepts", "author": "Abraham Silberschatz", "category": "Database", "description": "Fundamentals of database architecture and SQL query engine.", "copies": 3},
    {"title": "SQL Practice Problems", "author": "Sylvia Moestl", "category": "Database", "description": "57 hands-on SQL queries to improve database skills.", "copies": 5},
    {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "category": "Database", "description": "The bible of storage, replication, and distributed databases.", "copies": 4},
    {"title": "Database Design for Mere Mortals", "author": "Michael Hernandez", "category": "Database", "description": "A straightforward guide to relational database design.", "copies": 3},
    {"title": "Learning SQL", "author": "Alan Beaulieu", "category": "Database", "description": "Introductory SQL querying and database CRUD structures.", "copies": 4},
    {"title": "High Performance MySQL", "author": "Silvia Botros", "category": "Database", "description": "Optimizing MySQL server performance, index structures, and replication.", "copies": 2},
    {"title": "NoSQL Distilled", "author": "Pramod Sadalage", "category": "Database", "description": "A brief guide to the emerging world of polyglot persistence.", "copies": 3},
    {"title": "PostgreSQL: Up and Running", "author": "Regina Obe", "category": "Database", "description": "Practical guide to PostgreSQL database management.", "copies": 2},
    {"title": "SQL Performance Explained", "author": "Markus Winand", "category": "Database", "description": "Essential index tuning for database developer performance.", "copies": 3},
    {"title": "Relational Database Theory", "author": "David Maier", "category": "Database", "description": "Mathematical foundations of database relations.", "copies": 1},
    {"title": "Graph Databases", "author": "Ian Robinson", "category": "Database", "description": "Storing relationships natively in Neo4j graph schemas.", "copies": 2},
    {"title": "MongoDB: The Definitive Guide", "author": "Shannon Bradshaw", "category": "Database", "description": "Guide to MongoDB document database architecture.", "copies": 3},

    
    {"title": "Computer Networking: A Top-Down Approach", "author": "Kurose & Ross", "category": "Networking", "description": "Standard top-down approach to internet protocols.", "copies": 4},
    {"title": "TCP/IP Illustrated, Vol. 1", "author": "W. Richard Stevens", "category": "Networking", "description": "Detailed visual protocols analysis of TCP/IP.", "copies": 2},
    {"title": "Computer Networks", "author": "Andrew Tanenbaum", "category": "Networking", "description": "Detailed explanation of network layers and architectures.", "copies": 3},
    {"title": "Network Security Essentials", "author": "William Stallings", "category": "Networking", "description": "Principles and practice of cryptography and firewall security.", "copies": 3},
    {"title": "Wireshark Network Analysis", "author": "Laura Chappell", "category": "Networking", "description": "Master packet analysis and troubleshooting using Wireshark.", "copies": 2},
    {"title": "DNS and BIND", "author": "Cricket Liu", "category": "Networking", "description": "The absolute guide to internet domain naming and BIND.", "copies": 2},
    {"title": "High Performance Browser Networking", "author": "Ilya Grigorik", "category": "Networking", "description": "Optimizing browser loading protocols for web applications.", "copies": 3},
    {"title": "CCNA Routing and Switching", "author": "Todd Lammle", "category": "Networking", "description": "Comprehensive review guide for Cisco CCNA certification.", "copies": 4},
    {"title": "HTTP: The Definitive Guide", "author": "David Gourley", "category": "Networking", "description": "Protocols and architecture of the World Wide Web.", "copies": 25},
    {"title": "IPv6 Essentials", "author": "Silvia Hagen", "category": "Networking", "description": "Detailed introduction to the next-generation internet protocol.", "copies": 2},
    {"title": "Network Algorithmics", "author": "George Varghese", "category": "Networking", "description": "Fast packet processing techniques in hardware router design.", "copies": 1},
    {"title": "Software Defined Networks", "author": "Ken Gray", "category": "Networking", "description": "An authoritative review of OpenFlow and SDN architectures.", "copies": 2},

    
    {"title": "Artificial Intelligence: A Modern Approach", "author": "Russell & Norvig", "category": "AI/ML", "description": "The definitive textbook on agents, search, and neural networks.", "copies": 3},
    {"title": "Hands-On Machine Learning", "author": "Aurélien Géron", "category": "AI/ML", "description": "Scikit-Learn, Keras, and TensorFlow models construction.", "copies": 4},
    {"title": "Pattern Recognition and Machine Learning", "author": "Christopher Bishop", "category": "AI/ML", "description": "Comprehensive Bayesian approach to machine learning models.", "copies": 2},
    {"title": "Deep Learning", "author": "Goodfellow, Bengio, Courville", "category": "AI/ML", "description": "The bible of deep feedforward networks and convolutional nets.", "copies": 3},
    {"title": "Speech and Language Processing", "author": "Daniel Jurafsky", "category": "AI/ML", "description": "Classic textbook on NLP, speech recognition, and language models.", "copies": 2},
    {"title": "Reinforcement Learning", "author": "Sutton & Barto", "category": "AI/ML", "description": "Comprehensive introduction to Markov decision processes and Q-learning.", "copies": 2},
    {"title": "Introduction to Statistical Learning", "author": "Gareth James", "category": "AI/ML", "description": "Practical machine learning applications with R libraries.", "copies": 4},
    {"title": "The Elements of Statistical Learning", "author": "Hastie, Tibshirani, Friedman", "category": "AI/ML", "description": "Mathematical framework of classification and regression.", "copies": 2},
    {"title": "Programming Collective Intelligence", "author": "Toby Segaran", "category": "AI/ML", "description": "Building web crawlers, search engines, and collaborative filters.", "copies": 3},
    {"title": "Neural Networks and Deep Learning", "author": "Michael Nielsen", "category": "AI/ML", "description": "An online free book explaining core neural network logic.", "copies": 3},
    {"title": "Computer Vision: Algorithms and Applications", "author": "Richard Szeliski", "category": "AI/ML", "description": "Principles and algorithms of digital image processing.", "copies": 2},
    {"title": "Natural Language Processing with Python", "author": "Steven Bird", "category": "AI/ML", "description": "Analyzing text structure and grammar patterns using NLTK.", "copies": 3},

    
    {"title": "Introduction to Linear Algebra", "author": "Gilbert Strang", "category": "Mathematics", "description": "The absolute guide to vector spaces, matrices, and eigenvalues.", "copies": 4},
    {"title": "Concrete Mathematics", "author": "Graham, Knuth, Patashnik", "category": "Mathematics", "description": "Foundation mathematical coursework for computer science.", "copies": 2},
    {"title": "Calculus", "author": "Michael Spivak", "category": "Mathematics", "description": "An introduction to rigorous mathematical analysis.", "copies": 2},
    {"title": "Linear Algebra Done Right", "author": "Sheldon Axler", "category": "Mathematics", "description": "Modern operator-based approach to vector spaces.", "copies": 3},
    {"title": "Probability and Random Processes", "author": "Grimmett & Stirzaker", "category": "Mathematics", "description": "Standard university course on probability models.", "copies": 2},
    {"title": "All of Statistics", "author": "Larry Wasserman", "category": "Mathematics", "description": "A concise course in statistical inference and modeling.", "copies": 3},
    {"title": "Discrete Mathematics and its Applications", "author": "Kenneth Rosen", "category": "Mathematics", "description": "Logic, graphs, set theory, and counting methods.", "copies": 4},
    {"title": "A Book of Abstract Algebra", "author": "Charles Pinter", "category": "Mathematics", "description": "Excellent friendly guide to groups, rings, and fields.", "copies": 3},
    {"title": "Real Mathematical Analysis", "author": "Charles Pugh", "category": "Mathematics", "description": "Clear geometrical explanations of metric spaces.", "copies": 2},
    {"title": "Graph Theory", "author": "Reinhard Diestel", "category": "Mathematics", "description": "Advanced mathematical study of graphs.", "copies": 2},
    {"title": "Numerical Recipes", "author": "William Press", "category": "Mathematics", "description": "Practical scientific computing and calculations in C++.", "copies": 2},
    {"title": "Introduction to Mathematical Logic", "author": "Elliott Mendelson", "category": "Mathematics", "description": "Classic textbook on formal logic systems.", "copies": 1},

    
    {"title": "Design Patterns", "author": "Gamma, Helm, Johnson, Vlissides", "category": "Software Engineering", "description": "Classic gang of four catalog of object design patterns.", "copies": 2},
    {"title": "Refactoring", "author": "Martin Fowler", "category": "Software Engineering", "description": "Improving the design of existing code bases.", "copies": 3},
    {"title": "Clean Code", "author": "Robert C. Martin", "category": "Software Engineering", "description": "Agile software craftsmanship guidelines for developers.", "copies": 4},
    {"title": "The Clean Coder", "author": "Robert C. Martin", "category": "Software Engineering", "description": "A code of conduct for professional programmers.", "copies": 3},
    {"title": "Clean Architecture", "author": "Robert C. Martin", "category": "Software Engineering", "description": "A craftsman's guide to software structure and design.", "copies": 4},
    {"title": "Working Effectively with Legacy Code", "author": "Michael Feathers", "category": "Software Engineering", "description": "How to make modifications to code without breaking it.", "copies": 2},
    {"title": "Test Driven Development: By Example", "author": "Kent Beck", "category": "Software Engineering", "description": "Write cleaner code through test-first programming.", "copies": 3},
    {"title": "Domain-Driven Design", "author": "Eric Evans", "category": "Software Engineering", "description": "Tackling software complexity in the heart of business logic.", "copies": 2},
    {"title": "Continuous Delivery", "author": "Jez Humble", "category": "Software Engineering", "description": "Reliable software releases through build pipeline automation.", "copies": 2},
    {"title": "The Unicorn Project", "author": "Gene Kim", "category": "Software Engineering", "description": "A novel about developers, DevOps, and business success.", "copies": 3},
    {"title": "Software Engineering at Google", "author": "Titus Winters", "category": "Software Engineering", "description": "Lessons learned from Google software scale over time.", "copies": 3},
    {"title": "Pragmatic Thinking and Learning", "author": "Andy Hunt", "category": "Software Engineering", "description": "Refactor your wetware to think and learn faster.", "copies": 2},

    
    {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "category": "General", "description": "Explores the history of humanity from stone age to modern day.", "copies": 5},
    {"title": "Gödel, Escher, Bach: An Eternal Golden Braid", "author": "Douglas Hofstadter", "category": "General", "description": "A metaphorical fugue on minds and machines.", "copies": 2},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "category": "General", "description": "Classic guide to black holes, relativity, and the cosmos.", "copies": 4},
    {"title": "Surely You're Joking, Mr. Feynman!", "author": "Richard Feynman", "category": "General", "description": "Adventures of a curious theoretical physicist.", "copies": 3},
    {"title": "The Innovators", "author": "Walter Isaacson", "category": "General", "description": "How a group of hackers, geniuses, and geeks created the digital revolution.", "copies": 3},
    {"title": "Steve Jobs", "author": "Walter Isaacson", "category": "General", "description": "The exclusive biography of the Apple co-founder.", "copies": 4},
    {"title": "Atomic Habits", "author": "James Clear", "category": "General", "description": "Easy and proven way to build good habits and break bad ones.", "copies": 6},
    {"title": "Deep Work", "author": "Cal Newport", "category": "General", "description": "Rules for focused success in a distracted world.", "copies": 5},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "category": "General", "description": "Explains the two systems that drive our decision making.", "copies": 4},
    {"title": "Zero to One", "author": "Peter Thiel", "category": "General", "description": "Notes on startups, or how to build the future.", "copies": 5},
    {"title": "Elon Musk", "author": "Walter Isaacson", "category": "General", "description": "The biography of the controversial tech billionaire.", "copies": 3},
    {"title": "The Pragmatic Programmer", "author": "David Thomas", "category": "General", "description": "Mastering coding craft from journey to mastery.", "copies": 3},
    {"title": "Outliers: The Story of Success", "author": "Malcolm Gladwell", "category": "General", "description": "Explores why some people achieve extraordinary success.", "copies": 4},
    {"title": "Blink: The Power of Thinking Without Thinking", "author": "Malcolm Gladwell", "category": "General", "description": "Visual intuition and rapid decision making.", "copies": 3},
    {"title": "Superintelligence", "author": "Nick Bostrom", "category": "General", "description": "Paths, dangers, and strategies of abstract artificial intelligence.", "copies": 2},
    {"title": "Zero: The Biography of a Dangerous Idea", "author": "Charles Seife", "category": "General", "description": "Explores the origins and power of the number zero.", "copies": 3}
]

def seed_database():
    try:
        conn = get_db()
        cur = conn.cursor()
    except Exception as e:
        print(f"[Seed] Database connection error: {e}")
        return
        
    print("[Seed] Truncating existing catalog...")
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE books")
        cur.execute("TRUNCATE TABLE transactions")
        cur.execute("TRUNCATE TABLE queue")
        cur.execute("TRUNCATE TABLE reviews")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("  -> Truncated tables books, transactions, queue, reviews.")
    except Exception as e:
        print(f"[Seed] Truncation failed: {e}")
        cur.close(); conn.close()
        return

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[Seed] Warning: GEMINI_API_KEY not found in environment. Books will be seeded without embeddings.")
        
    print(f"[Seed] Seeding {len(books_data)} books into catalog...")
    inserted_count = 0
    
    for bk in books_data:
        title = bk['title']
        author = bk['author']
        cat = bk['category']
        desc = bk['description']
        copies = bk['copies']
        
        embedding_json = None
        if api_key:
            text = f"{title} by {author}. Category: {cat}. {desc}"
            emb = get_embedding(text)
            if emb:
                embedding_json = json.dumps(emb)
                
        try:
            cur.execute("""
                INSERT INTO books (title, author, category, total_copies, available, description, embedding) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (title, author, cat, copies, copies, desc, embedding_json))
            inserted_count += 1
            if inserted_count % 10 == 0:
                print(f"  -> Inserted {inserted_count} books...")
        except Exception as e:
            print(f"  -> Failed to insert '{title}': {e}")
            
    conn.commit()
    cur.close(); conn.close()
    print(f"[Seed] Finished! Successfully inserted {inserted_count} library books.")

if __name__ == '__main__':
    seed_database()
