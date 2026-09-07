import os
import re
from typing import List, Dict, Any, Optional, Tuple
from models import (
    ChatRequest, ChatResponse,
    ExplainRequest, ExplainResponse, LineExplanation,
    DebugRequest, DebugResponse
)

# Optional API integration if user configures .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Comprehensive catalog of curated programming topics with 3 difficulty tiers,
# check questions, 3 progressive hints, and practice challenges.
TUTOR_TOPICS: Dict[str, Dict[str, Any]] = {
    "variables": {
        "title": "Variables & Data Types",
        "keywords": ["variable", "variables", "data type", "int", "float", "string type", "boolean", "assign", "assignment", "declare", "declaration", "var ", "let ", "const "],
        "beginner": {
            "concept": "A **variable** is like a labelled box that stores a value in the computer's memory. You give the box a name, put something inside, and retrieve it whenever you need it!",
            "code": "# Storing different kinds of data\nname = 'Alice'       # str  - text\nage  = 20            # int  - whole number\ngpa  = 3.85          # float - decimal\nis_student = True    # bool - True / False\n\nprint(f'{name} is {age} years old.')  # Alice is 20 years old.",
            "question": "What is the data type of the value `3.14`—is it an `int`, `float`, or `str`?",
            "hint1": "Does `3.14` contain a decimal point?",
            "hint2": "Numbers with decimal points belong to a different type than whole numbers.",
            "hint3": "Any number with a decimal (`.`) is a `float`. Whole numbers like `3` are `int`.",
            "answer_keywords": ["float", "floating point", "decimal"],
            "answer_explanation": "Correct! `3.14` is a `float` because it has a decimal component. Python automatically infers types—no need to declare them explicitly.",
            "challenge": "Create variables for your name, age, and favourite language, then print a one-line summary using an f-string."
        },
        "intermediate": {
            "concept": "**Dynamic Typing & Name Binding**: In Python, variables are references (pointers) to objects on the heap—not typed containers. The same name can rebind to a completely different object at any time.",
            "code": "x = 42          # x points to int object 42\nx = 'hello'     # x now points to str object—no error!\nx = [1, 2, 3]   # x points to list—Python is dynamically typed\n\n# Check type at runtime\nprint(type(x))   # <class 'list'>",
            "question": "Why can reassigning `x = 'hello'` after `x = 42` cause subtle bugs, and how does `isinstance()` help?",
            "hint1": "Think about what happens when a function expects a number but receives a string.",
            "hint2": "`isinstance(x, int)` lets you guard against unexpected types at runtime.",
            "hint3": "Dynamic typing means the bug only surfaces at runtime, not at compile time. Type checks or type hints catch issues early.",
            "answer_keywords": ["isinstance", "type check", "runtime", "type hint", "annotation"],
            "answer_explanation": "Exactly! Python rebinds silently, so downstream code expecting an `int` crashes with a `str`. `isinstance()` guards + type hints (`x: int`) surface problems early.",
            "challenge": "Write a function `safe_add(a, b)` that raises `TypeError` with a helpful message if either argument is not a number."
        },
        "advanced": {
            "concept": "**CPython Object Model**: Every Python value is a `PyObject` C struct with a reference count, type pointer, and value payload. Variable assignment increments the object's `ob_refcnt`; deletion decrements it—triggering GC when it reaches zero.",
            "code": "import sys\nx = [1, 2, 3]\nprint(sys.getrefcount(x))  # 2 (one extra for getrefcount's arg frame)\ny = x                       # same object, refcount += 1\ndel y                       # refcount -= 1, object not freed yet\ndel x                       # refcount -> 0 → object freed by GC",
            "question": "What memory problem can arise when two objects each hold a reference to the other, and how does CPython's cyclic garbage collector resolve it?",
            "hint1": "If object A references B and B references A, will their reference counts ever reach zero through normal refcounting?",
            "hint2": "This is a reference cycle—standard refcounting cannot collect it.",
            "hint3": "CPython's `gc` module runs a mark-and-sweep collector periodically to detect and break reference cycles.",
            "answer_keywords": ["reference cycle", "cyclic", "gc module", "garbage collector", "mark and sweep"],
            "answer_explanation": "Brilliant! Mutual references keep `ob_refcnt > 0` forever. CPython's generational cyclic GC (`gc.collect()`) traces the object graph to find and free isolated cycles.",
            "challenge": "Use the `tracemalloc` module to capture a memory snapshot before and after creating 100 000 small objects, then report peak memory usage."
        }
    },
    "conditionals": {
        "title": "Conditionals (if / elif / else)",
        "keywords": ["if ", "elif", "else", "conditional", "condition", "branch", "branching", "ternary", "switch", "match "],
        "beginner": {
            "concept": "**Conditionals** let your program make decisions—like a fork in the road. The code checks a condition; if it is `True`, one path runs; if `False`, a different path runs.",
            "code": "temperature = 35  # degrees Celsius\n\nif temperature > 30:\n    print('It is hot! 🌞 Drink water.')\nelif temperature > 15:\n    print('It is warm. 🌤 Nice weather!')\nelse:\n    print('It is cool. 🧥 Grab a jacket.')",
            "question": "If `temperature = 20`, which branch executes and what will be printed?",
            "hint1": "Check the first condition: is 20 > 30?",
            "hint2": "The first condition is False. Now check the `elif`: is 20 > 15?",
            "hint3": "20 > 15 is True, so Python executes only the `elif` block.",
            "answer_keywords": ["elif", "warm", "nice weather", "20 > 15"],
            "answer_explanation": "Correct! Python evaluates conditions top-to-bottom and runs the first `True` branch. Since 20 > 15 is True, 'It is warm. 🌤 Nice weather!' prints.",
            "challenge": "Write an if/elif/else chain that classifies a test score (0-100) as Fail (<50), Pass (50-69), Merit (70-84), or Distinction (85+)."
        },
        "intermediate": {
            "concept": "**Short-Circuit Evaluation**: Python evaluates `and`/`or` lazily. In `A and B`, if `A` is `False`, `B` is never evaluated. In `A or B`, if `A` is `True`, `B` is skipped. This is exploited for safe default values.",
            "code": "# Guard against None before calling .upper()\nname = None\ndisplay = name and name.upper()  # name is False-y → short circuits to None\nprint(display)  # None (no AttributeError!)\n\n# Default value pattern with 'or'\nconfig = {}\ntimeout = config.get('timeout') or 30  # falls back to 30",
            "question": "What does `0 or 'default'` evaluate to, and why?",
            "hint1": "Is `0` considered truthy or falsy in Python?",
            "hint2": "Python treats `0`, `None`, `''`, `[]`, `{}` as falsy. So `0 or X` will evaluate `X`.",
            "hint3": "`0` is falsy, so `or` moves to the right operand `'default'` and returns it.",
            "answer_keywords": ["default", "falsy", "0 is falsy", "returns default"],
            "answer_explanation": "Exactly! `0` is falsy, so `0 or 'default'` short-circuits to `'default'`. This is Python's idiomatic fallback-value pattern.",
            "challenge": "Write a one-liner using a conditional expression (ternary) that clamps a number `n` to the range [0, 100]."
        },
        "advanced": {
            "concept": "**Structural Pattern Matching (Python 3.10+)**: `match/case` performs structural decomposition of objects, sequences, and mappings—far more powerful than chained `if/elif`. Guards (`if` clauses inside `case`) add extra predicates.",
            "code": "def http_status(code):\n    match code:\n        case 200:\n            return 'OK'\n        case 404:\n            return 'Not Found'\n        case 500 | 503:\n            return 'Server Error'\n        case c if 400 <= c < 500:\n            return f'Client Error {c}'\n        case _:\n            return 'Unknown'",
            "question": "How does `match/case` differ from a plain `dict` dispatch table in terms of capability and use cases?",
            "hint1": "A dict maps keys to callables—useful for exact lookups. What can `match` do that a dict cannot?",
            "hint2": "Pattern matching can destructure tuples, lists, and dataclass fields, and include guard conditions.",
            "hint3": "`match` supports deep structural decomposition, wildcard capture, and guard clauses—impossible with a plain dict.",
            "answer_keywords": ["destructure", "structural", "guard", "wildcard", "decompose", "capture"],
            "answer_explanation": "Superb! Dict dispatch handles exact key lookups efficiently. `match` excels at structural decomposition, nested pattern binding, and conditional guards—patterns a dict cannot express.",
            "challenge": "Use `match/case` to parse a simple command string like `'move 5 north'` into a structured action dict `{'action': 'move', 'amount': 5, 'direction': 'north'}`."
        }
    },
    "strings": {
        "title": "Strings & Text Processing",
        "keywords": ["string", "strings", "str", "text", "substring", "f-string", "format", "concatenat", "split", "join", "replace", "strip", "upper", "lower"],
        "beginner": {
            "concept": "A **string** is a sequence of characters (letters, digits, symbols) enclosed in quotes. You can join strings, extract parts, change case, and check contents with simple built-in methods.",
            "code": "greeting = 'Hello, World!'\n\nprint(greeting.upper())       # 'HELLO, WORLD!'\nprint(greeting.lower())       # 'hello, world!'\nprint(greeting[0:5])          # 'Hello'  (slicing)\nprint(len(greeting))          # 13  (length)",
            "question": "What does `'Python'[2]` return, and what is `'Python'[-1]`?",
            "hint1": "Remember indexing starts at 0. Count characters: P=0, y=1, t=2...",
            "hint2": "`'Python'[2]` accesses the character at position 2.",
            "hint3": "`'Python'[2]` → `'t'`. Negative index `-1` accesses the last character → `'n'`.",
            "answer_keywords": ["t", "n", "'t'", "'n'"],
            "answer_explanation": "Spot on! Index 2 is `'t'`, and `-1` is a convenient shortcut for the last character `'n'`.",
            "challenge": "Write a function `is_palindrome(s)` that returns `True` if the string reads the same forwards and backwards (ignore case)."
        },
        "intermediate": {
            "concept": "**String Immutability & Interning**: Strings in Python are immutable objects. Every operation like `+` creates a new string in memory. For bulk concatenation, `''.join(parts)` is O(N) vs. repeated `+` which is O(N²).",
            "code": "words = ['Hello', 'World', 'from', 'Python']\n\n# Efficient: join builds the string in one pass\nresult = ' '.join(words)\nprint(result)   # 'Hello World from Python'\n\n# Pattern: split → transform → join\ncsv = 'alice,bob,charlie'\nnames = [n.title() for n in csv.split(',')]\nprint(', '.join(names))  # 'Alice, Bob, Charlie'",
            "question": "Why is `''.join(list_of_strings)` faster than concatenating strings in a loop with `+`?",
            "hint1": "Think about what happens to memory each time you do `result = result + new_str`.",
            "hint2": "Each `+` allocates a brand-new string object of the combined size.",
            "hint3": "`join` pre-calculates total length, allocates memory once, then fills it—O(N). Repeated `+` reallocates each time—O(N²).",
            "answer_keywords": ["one allocation", "o(n)", "o(n2)", "reallocate", "join allocates once"],
            "answer_explanation": "Exactly right! `join` computes total length first and allocates once. Repeated `+` creates a new string on every iteration—quadratic overhead.",
            "challenge": "Write a function that takes a sentence and returns a dictionary counting how many times each word appears (case-insensitive)."
        },
        "advanced": {
            "concept": "**Unicode, Encoding & Bytes**: Python `str` is a sequence of Unicode code points. On disk or in a network packet, text must be **encoded** to bytes (e.g., UTF-8). Confusing `str` and `bytes` causes `UnicodeDecodeError` and security issues.",
            "code": "text = 'Héllo'          # str: Unicode code points\nbytes_utf8 = text.encode('utf-8')   # bytes: b'H\\xc3\\xa9llo'\nback_to_str = bytes_utf8.decode('utf-8')  # str again\n\nprint(len(text))       # 5 code points\nprint(len(bytes_utf8)) # 6 bytes (é = 2 bytes in UTF-8)",
            "question": "Why might `len('é') == 1` but `len('é'.encode('utf-8')) == 2`? What does this imply for byte-level string processing?",
            "hint1": "Python `len(str)` counts Unicode code points, not bytes.",
            "hint2": "UTF-8 encodes non-ASCII code points using 2-4 bytes each.",
            "hint3": "`len(str)` counts characters (code points); `len(bytes)` counts raw bytes. Byte-level ops on encoded UTF-8 can split multi-byte sequences, corrupting text.",
            "answer_keywords": ["code point", "utf-8", "multi-byte", "byte length", "character length"],
            "answer_explanation": "Exceptional! `len(str)` measures code points; `len(bytes)` measures raw octets. Slicing encoded bytes mid-character produces `UnicodeDecodeError`—always decode before slicing.",
            "challenge": "Write a function that safely truncates a UTF-8 encoded byte string to at most `max_bytes` bytes without splitting a multi-byte character."
        }
    },
    "error_handling": {
        "title": "Error Handling (try / except / finally)",
        "keywords": ["try", "except", "exception", "error", "raise", "finally", "valueerror", "typeerror", "keyerror", "indexerror", "catch", "throw", "handle"],
        "beginner": {
            "concept": "**Error handling** prevents your program from crashing when something unexpected happens. You *try* risky code, *except* (catch) the error if it happens, and respond gracefully instead of stopping the program.",
            "code": "try:\n    number = int(input('Enter a number: '))\n    result = 100 / number\n    print(f'100 / {number} = {result}')\nexcept ValueError:\n    print('❌ That was not a valid number!')\nexcept ZeroDivisionError:\n    print('❌ Cannot divide by zero!')\nfinally:\n    print('✅ Calculation attempt complete.')",
            "question": "Does the `finally` block run if an exception occurs and is caught by `except`?",
            "hint1": "Think of `finally` as 'always happens no matter what'.",
            "hint2": "`finally` executes whether an exception was raised or not, and whether it was caught or not.",
            "hint3": "Yes! `finally` **always** runs—it's used for cleanup like closing files or database connections.",
            "answer_keywords": ["yes", "always", "always runs", "runs always", "cleanup"],
            "answer_explanation": "Spot on! `finally` always executes regardless of exceptions—perfect for cleanup code like closing files or releasing locks.",
            "challenge": "Write a function `safe_read_file(path)` that returns the file's text content or an empty string if the file is missing, using try/except."
        },
        "intermediate": {
            "concept": "**Exception Hierarchy & Custom Exceptions**: Python exceptions form a class hierarchy (`BaseException → Exception → ValueError…`). Catching a parent class catches all its children. Creating custom exceptions clarifies domain-specific error semantics.",
            "code": "class InsufficientFundsError(Exception):\n    def __init__(self, amount, balance):\n        super().__init__(f'Tried to withdraw {amount} but balance is only {balance}')\n        self.amount = amount\n        self.balance = balance\n\ndef withdraw(balance, amount):\n    if amount > balance:\n        raise InsufficientFundsError(amount, balance)\n    return balance - amount",
            "question": "Why is `except Exception` generally safer than `except BaseException`?",
            "hint1": "What other exceptions inherit from `BaseException` that you would NOT want to accidentally silence?",
            "hint2": "Think about `KeyboardInterrupt` (Ctrl+C) and `SystemExit`.",
            "hint3": "`BaseException` includes `KeyboardInterrupt` and `SystemExit`. Catching these silences user interrupts and `sys.exit()` calls—almost never desired.",
            "answer_keywords": ["keyboardinterrupt", "systemexit", "generatorexit", "silence", "interrupt"],
            "answer_explanation": "Exactly right! `BaseException` includes `KeyboardInterrupt` and `SystemExit`. Catching those prevents the user from stopping your program. `except Exception` is the safe default.",
            "challenge": "Create a custom `ValidationError` with a `field` and `message` attribute, then write a `validate_age(age)` function that raises it for invalid inputs."
        },
        "advanced": {
            "concept": "**Exception Chaining & Context**: Python 3 automatically chains exceptions via `__cause__` (explicit: `raise X from Y`) and `__context__` (implicit). This preserves the original traceback, which is critical for debugging layered systems.",
            "code": "def load_config(path):\n    try:\n        with open(path) as f:\n            import json\n            return json.load(f)\n    except (FileNotFoundError, json.JSONDecodeError) as e:\n        raise RuntimeError(f'Config load failed: {path}') from e  # chaining!",
            "question": "What is the difference between `raise X from Y` and `raise X from None`?",
            "hint1": "Both involve exception chaining—but one explicitly suppresses context.",
            "hint2": "`raise X from Y` sets `__cause__` and shows both tracebacks. `from None` suppresses the original.",
            "hint3": "`raise X from Y` preserves the cause in tracebacks. `raise X from None` hides the original exception (useful when the cause is an implementation detail users shouldn't see).",
            "answer_keywords": ["__cause__", "suppress", "hide", "context", "chain", "from none"],
            "answer_explanation": "Exceptional! `raise X from Y` chains tracebacks for full debugging context. `raise X from None` suppresses the internal cause—ideal when exposing implementation details would be confusing.",
            "challenge": "Build a context manager class using `__enter__` and `__exit__` that logs any exception to a file before re-raising it."
        }
    },
    "sorting": {
        "title": "Sorting Algorithms",
        "keywords": ["sort", "sorting", "bubble sort", "merge sort", "quick sort", "insertion sort", "selection sort", "sorted", "timsort", "order", "ascending", "descending"],
        "beginner": {
            "concept": "**Sorting** means arranging items in a specific order (smallest to largest, or A to Z). Python's built-in `sorted()` and `.sort()` handle this for you. Understanding the basics helps you know when to choose which approach.",
            "code": "numbers = [5, 2, 8, 1, 9, 3]\n\n# sorted() returns a NEW sorted list\nnew_list = sorted(numbers)\nprint(new_list)   # [1, 2, 3, 5, 8, 9]\n\n# .sort() modifies the list IN PLACE\nnumbers.sort(reverse=True)\nprint(numbers)    # [9, 8, 5, 3, 2, 1]",
            "question": "What is the key difference between `sorted(my_list)` and `my_list.sort()`?",
            "hint1": "Think about what happens to the original list in each case.",
            "hint2": "One creates a new list; the other modifies the existing list directly.",
            "hint3": "`sorted()` returns a new sorted list and leaves the original unchanged. `.sort()` modifies the list in-place and returns `None`.",
            "answer_keywords": ["new list", "in place", "in-place", "returns none", "original unchanged"],
            "answer_explanation": "Spot on! `sorted()` is non-destructive (returns new list). `.sort()` is in-place (modifies original, returns None). Choose based on whether you need the original preserved.",
            "challenge": "Given a list of student dictionaries `[{'name': 'Bob', 'score': 72}, ...]`, sort them by score descending using a `key` function."
        },
        "intermediate": {
            "concept": "**Merge Sort — Divide & Conquer**: Merge sort splits a list in half recursively until single elements remain, then merges sorted halves. It guarantees O(N log N) time in all cases and is **stable** (equal elements keep their original order).",
            "code": "def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left  = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i]); i += 1\n        else:\n            result.append(right[j]); j += 1\n    return result + left[i:] + right[j:]",
            "question": "Why is Merge Sort preferred over Bubble Sort for large datasets?",
            "hint1": "Compare their time complexities: Bubble Sort is O(N²), Merge Sort is O(N log N).",
            "hint2": "For 1 million elements: Bubble Sort ≈ 10^12 operations; Merge Sort ≈ 20 million.",
            "hint3": "O(N log N) grows far slower than O(N²). Merge Sort also has guaranteed worst-case performance, unlike Quick Sort.",
            "answer_keywords": ["o(n log n)", "o(n2)", "faster", "quadratic", "log n"],
            "answer_explanation": "Exactly! Bubble Sort is O(N²)—it becomes painfully slow on large data. Merge Sort's O(N log N) is many orders of magnitude faster and is stable.",
            "challenge": "Implement Binary Search on a sorted list. Given a target, return its index or -1 if not found—in O(log N) time."
        },
        "advanced": {
            "concept": "**Timsort — Python's Hybrid Algorithm**: Python's `sorted()` uses Timsort—a hybrid of Merge Sort and Insertion Sort. It identifies natural *runs* (already-sorted subsequences) and merges them. Timsort achieves O(N) on nearly-sorted data and O(N log N) worst-case.",
            "code": "# Timsort exploits existing order (real-world data often partially sorted)\nimport time\n\nalmost_sorted = list(range(10000)) + [9999, 5, 3]\nrandom_data   = list(range(9999, -1, -1))  # reversed\n\nstart = time.perf_counter()\nsorted(almost_sorted)\nprint(f'Nearly sorted: {time.perf_counter()-start:.6f}s')\n\nstart = time.perf_counter()\nsorted(random_data)\nprint(f'Reversed data: {time.perf_counter()-start:.6f}s')",
            "question": "When would you choose Radix Sort over Timsort, and what is Radix Sort's time complexity?",
            "hint1": "Radix Sort does not use comparisons—it operates on digit or character positions.",
            "hint2": "Comparison-based sorts have a lower bound of O(N log N). Non-comparison sorts can do better under certain constraints.",
            "hint3": "Radix Sort is O(N·k) where k = number of digits. It beats O(N log N) for large N with fixed-width integers or strings.",
            "answer_keywords": ["o(nk)", "non-comparison", "digit", "fixed width", "integers", "linear"],
            "answer_explanation": "Superb! Radix Sort bypasses the O(N log N) comparison lower bound by sorting digit-by-digit in O(N·k)—ideal for large sets of fixed-length integers or strings.",
            "challenge": "Implement counting sort for a list of integers in range [0, k] in O(N + k) time and compare its speed against Python's `sorted()` for k=1000, N=1 000 000."
        }
    },
    "data_structures": {
        "title": "Data Structures (Stack, Queue, Linked List)",
        "keywords": ["stack", "queue", "linked list", "node", "deque", "heap", "tree", "binary tree", "graph", "data structure", "push", "pop", "enqueue", "dequeue"],
        "beginner": {
            "concept": "A **Stack** is like a pile of plates—you can only add (push) or remove (pop) from the top. A **Queue** is like a line at a store—the first person in is the first one served (FIFO: First In, First Out).",
            "code": "# Stack using a Python list\nstack = []\nstack.append('task_1')  # push\nstack.append('task_2')\nstack.append('task_3')\nprint(stack.pop())  # 'task_3' — Last In, First Out (LIFO)\n\n# Queue using collections.deque\nfrom collections import deque\nqueue = deque()\nqueue.append('customer_1')  # enqueue\nqueue.append('customer_2')\nprint(queue.popleft())  # 'customer_1' — First In, First Out (FIFO)",
            "question": "Which data structure—Stack or Queue—does a web browser's Back button use, and why?",
            "hint1": "Think about the order pages are visited vs. the order the Back button navigates them.",
            "hint2": "When you press Back, the most recently visited page appears first.",
            "hint3": "A **Stack** (LIFO). The last page visited is the first one returned to when pressing Back.",
            "answer_keywords": ["stack", "lifo", "last in first out"],
            "answer_explanation": "Correct! Browser history is a Stack. Each new page is pushed; pressing Back pops the most recently visited page—classic LIFO behaviour.",
            "challenge": "Implement a function `is_balanced(s)` that checks if brackets in a string like `'({[]})'` are properly balanced, using a Stack."
        },
        "intermediate": {
            "concept": "**Linked List vs. Array**: A Linked List stores elements in nodes where each node holds a value and a pointer to the next node. Unlike arrays, insertions/deletions at the head are O(1), but random access is O(N) since you must traverse the chain.",
            "code": "class Node:\n    def __init__(self, value):\n        self.value = value\n        self.next  = None\n\nclass LinkedList:\n    def __init__(self):\n        self.head = None\n\n    def prepend(self, value):  # O(1) — no shifting needed!\n        new_node = Node(value)\n        new_node.next = self.head\n        self.head = new_node",
            "question": "When would you choose a Linked List over a Python list, given that lists support O(1) random access?",
            "hint1": "Think about operations where Linked Lists have an advantage: frequent insertions at arbitrary positions.",
            "hint2": "List insertions at position 0 require shifting N elements—O(N). Linked List head insertions are always O(1).",
            "hint3": "Use Linked Lists when you have very frequent insertions/deletions at the front or middle, and random access by index is rare.",
            "answer_keywords": ["frequent insert", "prepend", "o(1) insert", "no shifting", "middle insert"],
            "answer_explanation": "Exactly! Linked Lists shine for frequent O(1) head/tail insertions without element shifting. For random access or iteration, a Python list is faster due to CPU cache locality.",
            "challenge": "Implement a `reverse()` method for a singly Linked List that reverses the list in-place in O(N) time and O(1) auxiliary space."
        },
        "advanced": {
            "concept": "**Binary Heap & Priority Queue**: A Binary Heap is a complete binary tree satisfying the heap property (min-heap: parent ≤ children). Python's `heapq` implements a min-heap in a plain list with O(log N) push/pop and O(1) peek.",
            "code": "import heapq\n\n# Min-heap: smallest element always at index 0\npq = []\nheapq.heappush(pq, (5, 'task_low'))\nheapq.heappush(pq, (1, 'task_high'))\nheapq.heappush(pq, (3, 'task_medium'))\n\nwhile pq:\n    priority, task = heapq.heappop(pq)\n    print(f'Processing: {task} (priority {priority})')",
            "question": "Why is building a heap from N elements using `heapq.heapify()` O(N) rather than O(N log N)?",
            "hint1": "Heapify does not insert elements one by one—it uses a different algorithm.",
            "hint2": "It sifts down each non-leaf node. Most nodes are near the bottom and require very few swaps.",
            "hint3": "Heapify starts from the last internal node and sifts down. Lower nodes need fewer comparisons; the amortized total is O(N).",
            "answer_keywords": ["sift down", "heapify", "o(n)", "amortized", "non-leaf"],
            "answer_explanation": "Outstanding! `heapify` sifts down each subtree bottom-up. Nodes near the leaves need O(1) work, nodes near the root need O(log N). The sum telescopes to O(N) total.",
            "challenge": "Implement Dijkstra's shortest-path algorithm using Python's `heapq` for a weighted directed graph represented as an adjacency list."
        }
    },
    "operators": {
        "title": "Operators & Boolean Logic",
        "keywords": ["operator", "operators", "boolean", "and", "or", "not", "modulo", "modulus", "bitwise", "comparison", "==", "!=", "greater", "less than", "truthy", "falsy"],
        "beginner": {
            "concept": "**Operators** are symbols that tell Python to perform operations. Arithmetic operators do math; comparison operators compare values and return `True` or `False`; logical operators combine conditions.",
            "code": "# Arithmetic\nprint(10 + 3)   # 13  (addition)\nprint(10 - 3)   # 7   (subtraction)\nprint(10 * 3)   # 30  (multiplication)\nprint(10 / 3)   # 3.333... (true division)\nprint(10 // 3)  # 3   (floor division)\nprint(10 % 3)   # 1   (modulo — remainder)\nprint(2 ** 8)   # 256 (exponentiation)\n\n# Comparison → returns bool\nprint(5 > 3)    # True\nprint(5 == 5)   # True\nprint(5 != 3)   # True",
            "question": "What does `17 % 5` return, and what real-world problem can the modulo operator `%` solve?",
            "hint1": "Modulo returns the **remainder** after division. 17 ÷ 5 = 3 remainder...?",
            "hint2": "17 = 5 × 3 + 2. So the remainder is 2.",
            "hint3": "`17 % 5 = 2`. Modulo is used to check divisibility (`n % 2 == 0` means even), wrap around arrays, and build cyclic counters.",
            "answer_keywords": ["2", "remainder 2", "modulo", "remainder"],
            "answer_explanation": "Correct! `17 % 5 = 2`. Modulo is powerful for: checking even/odd numbers, wrapping array indices cyclically, and many algorithm problems.",
            "challenge": "Using only the `%` operator, write a function `fizzbuzz(n)` that returns 'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both, else the number."
        },
        "intermediate": {
            "concept": "**Bitwise Operators**: Work directly on binary bit patterns. `&` (AND), `|` (OR), `^` (XOR), `~` (NOT), `<<` (left shift), `>>` (right shift). They are extremely fast and used in flags, permissions, hashing, and graphics.",
            "code": "a = 0b1010  # 10 in decimal\nb = 0b1100  # 12 in decimal\n\nprint(bin(a & b))  # 0b1000 → 8  (AND)\nprint(bin(a | b))  # 0b1110 → 14 (OR)\nprint(bin(a ^ b))  # 0b0110 → 6  (XOR)\n\n# Fast multiply/divide by power of 2\nprint(3 << 2)  # 3 * 4 = 12\nprint(16 >> 1) # 16 / 2 = 8",
            "question": "How can you use the XOR (`^`) operator to swap two integers without a temporary variable?",
            "hint1": "XOR has a property: `a ^ a == 0` and `a ^ 0 == a`. Can you chain them?",
            "hint2": "`a = a ^ b; b = a ^ b` — what does `b` now equal?",
            "hint3": "`a ^= b; b ^= a; a ^= b` — XOR's self-inverse property swaps values without a temp variable.",
            "answer_keywords": ["xor", "a ^= b", "swap", "no temp", "no temporary"],
            "answer_explanation": "Brilliant! `a ^= b; b ^= a; a ^= b` exploits XOR's self-inverse property to swap in-place. Note: Python tuple swap `a, b = b, a` is cleaner in practice.",
            "challenge": "Use bitwise operations to implement a function `count_set_bits(n)` that counts how many 1-bits are in `n` (population count / Hamming weight)."
        },
        "advanced": {
            "concept": "**Operator Overloading via Dunder Methods**: Python operators are backed by special methods (`__add__`, `__eq__`, `__lt__`, etc.). By implementing these in your class, you define custom behaviour for `+`, `==`, `<`, `in`, and all other operators.",
            "code": "class Vector:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\n    def __add__(self, other):          # v1 + v2\n        return Vector(self.x + other.x, self.y + other.y)\n\n    def __repr__(self):\n        return f'Vector({self.x}, {self.y})'\n\nv1 = Vector(1, 2)\nv2 = Vector(3, 4)\nprint(v1 + v2)  # Vector(4, 6)",
            "question": "What dunder method should you implement to make your class work correctly with Python's `sorted()` function, and what complementary methods should accompany it?",
            "hint1": "Python's `sorted()` needs to compare objects. Which dunder enables `<` comparisons?",
            "hint2": "Implement `__lt__` for less-than. But `functools.total_ordering` can auto-derive the rest.",
            "hint3": "Implement `__lt__` and `__eq__`, then `@functools.total_ordering` auto-derives `__le__`, `__gt__`, `__ge__`.",
            "answer_keywords": ["__lt__", "total_ordering", "__eq__", "comparison", "dunder"],
            "answer_explanation": "Superb! Implement `__lt__` and `__eq__`, then decorate with `@functools.total_ordering` to automatically derive all six comparison operators for use with `sorted()`, `min()`, `max()`, etc.",
            "challenge": "Build a `Matrix` class supporting `*` (matrix multiplication via `__matmul__` / `@`), `+`, and `==` with full correctness checks."
        }
    },
    "type_conversion": {
        "title": "Type Conversion & Casting",
        "keywords": ["type conversion", "casting", "cast", "convert", "int()", "str()", "float()", "list()", "tuple", "implicit", "explicit", "coerce"],
        "beginner": {
            "concept": "**Type conversion** changes a value from one data type to another. Python has **implicit** conversion (automatic, safe) and **explicit** conversion (you call it yourself using built-in functions like `int()`, `str()`, `float()`).",
            "code": "# Explicit (manual) conversion\nage_str  = '25'\nage_int  = int(age_str)     # str → int\nprice    = float('19.99')   # str → float\nlabel    = str(42)           # int → str\n\nprint(age_int + 5)   # 30 (now arithmetic works!)\nprint('Price: ' + label)  # 'Price: 42'",
            "question": "What error does `'10' + 5` raise in Python, and how would you fix it?",
            "hint1": "Python does not automatically mix `str` and `int` in the `+` operator.",
            "hint2": "You need to convert one side so both are the same type.",
            "hint3": "It raises `TypeError`. Fix with `int('10') + 5 = 15` or `'10' + str(5) = '105'` depending on intent.",
            "answer_keywords": ["typeerror", "type error", "int('10')", "str(5)", "convert"],
            "answer_explanation": "Correct! Python raises `TypeError: can only concatenate str (not 'int') to str`. Convert with `int('10') + 5` for math, or `'10' + str(5)` for string concatenation.",
            "challenge": "Write a function `to_number(value)` that tries to convert a string to `int`, then `float`, and returns `None` if conversion is impossible—using try/except."
        },
        "intermediate": {
            "concept": "**Implicit Coercion & Truthy/Falsy**: Python implicitly treats many objects as `bool` in conditionals. Falsy values include `0`, `0.0`, `''`, `[]`, `{}`, `None`. Everything else is truthy. Understanding this avoids subtle bugs.",
            "code": "values = [0, '', None, [], 42, 'hello', [1, 2]]\n\n# Filter out falsy values\ntruthy = [v for v in values if v]\nprint(truthy)   # [42, 'hello', [1, 2]]\n\n# Common idiom: default value\nuser_input = ''\nname = user_input or 'Guest'  # '' is falsy → 'Guest'",
            "question": "Is an empty dictionary `{}` truthy or falsy in Python? What about a dictionary with one key?",
            "hint1": "Empty containers are generally falsy in Python.",
            "hint2": "Test it conceptually: `bool({})` — is an empty dict falsy like an empty list?",
            "hint3": "`{}` is **falsy** (empty). `{'key': 'value'}` is **truthy** (non-empty). Python's `bool()` delegates to `__len__` for containers.",
            "answer_keywords": ["falsy", "empty dict", "truthy", "non-empty", "bool"],
            "answer_explanation": "Exactly! `bool({})` is `False` (falsy). Any non-empty dict is `True`. Python calls `__len__()` and treats zero length as falsy—consistent across all built-in containers.",
            "challenge": "Write a function `deep_truthy(data)` that recursively removes falsy values from a nested dict/list structure."
        },
        "advanced": {
            "concept": "**`__bool__` & `__len__` Protocol**: Python calls `__bool__()` first (falling back to `__len__() != 0`) when evaluating truthiness. Implementing these in custom classes controls how objects behave in `if`, `while`, and boolean expressions.",
            "code": "class SafeBuffer:\n    def __init__(self, data):\n        self._data = data\n\n    def __len__(self):\n        return len(self._data)\n\n    def __bool__(self):  # explicit truth test\n        return len(self._data) > 0\n\nbuf = SafeBuffer([])\nprint(bool(buf))  # False — empty buffer",
            "question": "If a class defines `__len__` but NOT `__bool__`, how does Python determine its truthiness?",
            "hint1": "Python has a fallback chain for truthiness evaluation.",
            "hint2": "After checking `__bool__`, Python looks for another dunder method.",
            "hint3": "Python falls back to `__len__`—if `__len__() == 0` the object is falsy; otherwise truthy. Without both, objects are always truthy.",
            "answer_keywords": ["__len__", "fallback", "len == 0", "falsy when zero"],
            "answer_explanation": "Excellent! Python's truth-value protocol: `__bool__` → `__len__` (0 = False) → always True. Defining only `__len__` still gives correct size-based truthiness.",
            "challenge": "Design an `Interval` class representing a numeric range `[a, b]`. Make it falsy if `a == b` (zero-width interval) and implement `__contains__` so `5 in Interval(1, 10)` works."
        }
    },
    "modules": {
        "title": "Modules, Packages & Imports",
        "keywords": ["import", "module", "modules", "package", "packages", "from import", "pip", "library", "__init__", "namespace", "__name__"],
        "beginner": {
            "concept": "A **module** is just a Python file containing reusable functions and variables. Python ships with a huge **standard library** of built-in modules. You bring them into your script with `import`.",
            "code": "import math                    # standard library module\nfrom random import randint     # import a specific function\n\nprint(math.sqrt(16))  # 4.0\nprint(math.pi)        # 3.14159...\n\ndice = randint(1, 6)\nprint(f'Rolled: {dice}')",
            "question": "What is the difference between `import math` and `from math import sqrt`?",
            "hint1": "Think about how you call the function after each import style.",
            "hint2": "With `import math` you write `math.sqrt()`. With `from math import sqrt` you write just `sqrt()`.",
            "hint3": "`import math` imports the module—you prefix everything (`math.sqrt`). `from math import sqrt` imports one name directly into your namespace (`sqrt()`).",
            "answer_keywords": ["namespace", "prefix", "math.sqrt", "directly", "module name"],
            "answer_explanation": "Spot on! `import math` keeps all names under the `math` namespace (avoids conflicts). `from math import sqrt` brings `sqrt` directly into scope (more convenient but can cause name clashes).",
            "challenge": "Create a module `geometry.py` with `circle_area(r)` and `rectangle_area(w, h)` functions, then import and use them in a separate `main.py`."
        },
        "intermediate": {
            "concept": "**`__name__` Guard & Package Structure**: The `if __name__ == '__main__':` guard prevents code from running when a file is imported as a module. A **package** is a directory with `__init__.py` that groups related modules.",
            "code": "# utils.py\ndef add(a, b):\n    return a + b\n\nif __name__ == '__main__':\n    # Runs only when utils.py is executed directly\n    # NOT when it is imported by another module\n    print(add(2, 3))   # 5",
            "question": "Why is `if __name__ == '__main__':` considered a best practice for reusable Python scripts?",
            "hint1": "Think about what happens when another script does `import utils`.",
            "hint2": "Without the guard, all top-level code in the module executes on import.",
            "hint3": "Without the guard, importing the module runs your test code, prints output, and potentially causes side effects in the importing script.",
            "answer_keywords": ["side effects", "import runs", "direct execution", "not run on import"],
            "answer_explanation": "Exactly! Without the guard, `import utils` executes all top-level code causing unintended side effects. The guard ensures only intended entry-point code runs when executing directly.",
            "challenge": "Create a package `shapes/` with `__init__.py`, `circle.py`, and `rectangle.py`. Export `Circle` and `Rectangle` classes from the package's `__init__.py`."
        },
        "advanced": {
            "concept": "**Import System Internals**: Python's import system uses **finders** and **loaders** (`importlib`). `sys.path` defines the search order. `sys.modules` caches imported modules so re-imports return the cached object. Custom finders enable loading from databases, zips, or network.",
            "code": "import sys\nimport importlib\n\n# Force reload a module (useful in REPL development)\nimport my_module\nimportlib.reload(my_module)\n\n# Inspect module cache\nprint('math' in sys.modules)   # True (already imported)\nprint(sys.modules['math'])      # <module 'math' from ...>",
            "question": "Why is `importlib.reload(module)` sometimes necessary in a live Python session, and what are its limitations?",
            "hint1": "In a running REPL, Python caches modules. If you modify the source file, the old code stays in memory.",
            "hint2": "Reload re-executes the module file, but objects created from the old module remain.",
            "hint3": "Reload re-executes source and rebinds names in the module's namespace, but existing references to old class/function objects are NOT updated—stale instances persist.",
            "answer_keywords": ["stale", "cache", "old reference", "existing instances", "namespace"],
            "answer_explanation": "Outstanding! `reload` re-runs the file and refreshes the module's namespace, but existing variables and instances that point to old class objects are not automatically updated—this limits hot-reloading in complex systems.",
            "challenge": "Write a custom import finder (implementing `find_module` and `load_module` or the newer `find_spec`/`exec_module`) that loads Python source files from a dictionary in memory."
        }
    },

    "loops": {
        "title": "Loops (For & While Iteration)",
        "keywords": ["loop", "loops", "for loop", "while loop", "iteration", "iterate", "range"],
        "beginner": {
            "concept": "A **loop** tells the computer to repeat instructions multiple times without duplicating code. Think of it like running laps around a sports track until you hit your target lap count!",
            "code": "# Repeating 3 times with a for loop\nfor lap in range(1, 4):\n    print(f'Running lap {lap}! 🏃')",
            "question": "If you change `range(1, 4)` to `range(1, 6)`, how many total times will the print statement execute?",
            "hint1": "Remember: `range(start, stop)` starts at `start` and stops *just before* `stop`.",
            "hint2": "Count the exact numbers visited: 1, 2, 3, 4, 5.",
            "hint3": "The sequence is [1, 2, 3, 4, 5]. How many numbers are in that list?",
            "answer_keywords": ["5", "five", "5 times", "five times"],
            "answer_explanation": "Spot on! `range(1, 6)` generates 1, 2, 3, 4, and 5—running the loop exactly 5 times.",
            "challenge": "Write a short loop that prints only the **even numbers** between 2 and 10."
        },
        "intermediate": {
            "concept": "**Loops & Iteration Protocols**: In Python, loops operate over iterable objects implementing `__iter__()` and `__next__()`. List comprehensions provide an expressive, bytecode-optimized alternative to manual accumulator loops.",
            "code": "# List comprehension filtering and transforming in one pass\nsquares = [x**2 for x in range(1, 6) if x % 2 == 0]\nprint(squares)  # Output: [4, 16]",
            "question": "What is the Big-O time complexity if you nest an inner loop of size N inside an outer loop of size N?",
            "hint1": "Think about how many total operations happen if the outer loop repeats N times, and on each pass, the inner loop also repeats N times.",
            "hint2": "You multiply the operations: N multiplied by N.",
            "hint3": "In Big-O notation, N * N is written as O(N²), quadratic time.",
            "answer_keywords": ["n^2", "n²", "quadratic", "o(n^2)", "o(n2)", "o(n²)"],
            "answer_explanation": "Exactly right! Nested loops running up to N iterations produce O(N²) quadratic time complexity.",
            "challenge": "Refactor a nested loop that searches for duplicates into a single-pass loop using a `set` to achieve O(N) time."
        },
        "advanced": {
            "concept": "**Iteration Mechanics & Memory Locality**: At bytecode level, CPython uses the `FOR_ITER` opcode popping from the value stack. For large datasets, generator expressions stream values lazily with O(1) memory overhead rather than allocating full collections in RAM.",
            "code": "# Generator pipeline: streaming 10 million items with O(1) auxiliary RAM\nstream = (x * 2 for x in range(10**7) if x % 3 == 0)\nprint(next(stream))  # Computes on-demand, no multi-GB array allocation",
            "question": "Why does traversing a 2D matrix row-by-row execute significantly faster on modern hardware than column-by-column, even though total element visits are identical?",
            "hint1": "Think about physical CPU architecture and how hardware caching works.",
            "hint2": "Consider CPU L1/L2 cache lines and spatial locality (contiguous memory addresses).",
            "hint3": "Row-major storage keeps adjacent row elements contiguous in memory, maximizing CPU cache line hits and eliminating cache misses.",
            "answer_keywords": ["cache", "spatial locality", "cache miss", "cache line", "contiguous", "row-major"],
            "answer_explanation": "Brilliant! Spatial cache locality allows consecutive row elements to load into CPU L1/L2 cache lines simultaneously, preventing expensive RAM bus stalls.",
            "challenge": "Implement a custom iterable class by defining `__iter__` and `__next__` that yields the Fibonacci sequence indefinitely without stack overflow."
        }
    },
    "recursion": {
        "title": "Recursion (Base Cases & Call Stacks)",
        "keywords": ["recursion", "recursive", "base case", "factorial", "call stack", "fibonacci"],
        "beginner": {
            "concept": "**Recursion** is when a function calls itself to solve a smaller piece of the same puzzle. Think of Russian nesting dolls: you open one, find a smaller one inside, and repeat until you hit the solid baby doll in the center!",
            "code": "def countdown(n):\n    if n <= 0:         # 1. Base Case: stop when n reaches 0\n        print('Blast off! 🚀')\n        return\n    print(n)\n    countdown(n - 1)   # 2. Recursive Call: smaller subproblem\n\ncountdown(3)  # Prints: 3, 2, 1, Blast off!",
            "question": "What happens if a recursive function forgets to include a base case (stopping condition)?",
            "hint1": "Think about what would happen if the countdown never checked `if n <= 0`.",
            "hint2": "The function would keep calling itself forever, filling up computer memory.",
            "hint3": "In programming, this infinite recursion causes a 'Stack Overflow' (or RecursionError in Python).",
            "answer_keywords": ["stack overflow", "infinite", "crashes", "crash", "recursionerror", "never stops", "forever"],
            "answer_explanation": "Spot on! Without a base case, the computer keeps adding function calls to memory until it crashes with a Stack Overflow (RecursionError).",
            "challenge": "Write a recursive function `sum_to(n)` that returns the sum of all numbers from 1 up to `n`."
        },
        "intermediate": {
            "concept": "**Stack Frame Mechanics in Recursion**: Each recursive invocation allocates an activation record (arguments, local variables, return address) on the Call Stack. Execution unwinds (pops) once the base condition returns.",
            "code": "def factorial(n: int) -> int:\n    # Base case: 0! = 1\n    if n <= 1:\n        return 1\n    # Recursive step: unwinds after hitting base case\n    return n * factorial(n - 1)",
            "question": "Why is naive recursive Fibonacci O(2^N) time complexity, and how do we optimize it to O(N)?",
            "hint1": "Look at a recursion tree for `fib(5)`—notice how many times `fib(3)` and `fib(2)` are re-calculated.",
            "hint2": "Think about caching or storing previously computed results.",
            "hint3": "We use **memoization** (dynamic programming) to store previous answers in a lookup table or `@lru_cache`.",
            "answer_keywords": ["memoization", "memo", "cache", "dynamic programming", "redundant", "overlapping", "lru_cache"],
            "answer_explanation": "Exactly right! Unmemoized recursion recalculates overlapping subproblems exponentially. Memoization caches sub-results to achieve O(N) linear time.",
            "challenge": "Use Python's `@functools.lru_cache` or a dictionary cache to write an O(N) memoized recursive Fibonacci solver."
        },
        "advanced": {
            "concept": "**Tail Call Optimization & Trampolining**: A function is strictly tail-recursive if the recursive call is the very last instruction before returning. In runtimes supporting TCO, the current stack frame is reused, reducing auxiliary stack space from O(N) to O(1).",
            "code": "# Tail-recursive accumulator pattern:\ndef factorial_tail(n: int, acc: int = 1) -> int:\n    if n <= 1:\n        return acc\n    # Tail call: no pending operations after recursive return\n    return factorial_tail(n - 1, acc * n)",
            "question": "Why does CPython intentionally omit Tail Call Optimization, and what pattern can you use to avoid stack overflows for deep recursive algorithms?",
            "hint1": "Consider Python's philosophy regarding debugging, stack traces, and tracebacks.",
            "hint2": "Guido van Rossum preserved stack frames so tracebacks remain complete. For deep recursion, consider turning the recursion into an iterative loop or using thunks.",
            "hint3": "The pattern is called a **trampoline** (or using an explicit heap-allocated stack).",
            "answer_keywords": ["traceback", "stack trace", "trampoline", "explicit stack", "heap", "debug"],
            "answer_explanation": "Exceptional insight! Guido chose to keep full stack tracebacks for debugging. To handle deep traversals without stack overflow, engineers use trampolining or explicit heap stacks.",
            "challenge": "Implement a generic `trampoline()` runner function that executes thunk-returning functions in constant stack space."
        }
    },
    "dictionaries": {
        "title": "Dictionaries & Hash Maps (Key-Value Lookups)",
        "keywords": ["dictionary", "dictionaries", "hashmap", "hash map", "hash table", "dict", "key value"],
        "beginner": {
            "concept": "A **Dictionary (or Hash Map)** is like a real-world phonebook or dictionary. Instead of index numbers (0, 1, 2) like a list, you look up data using unique **Keys**.",
            "code": "# Storing fruit prices\nprices = {'apple': 1.50, 'banana': 0.80, 'orange': 1.25}\n\n# Fast lookup by key!\nprint(prices['apple'])  # Prints: 1.50",
            "question": "What happens in Python if you try to access a key that does not exist using square brackets, like `prices['mango']`?",
            "hint1": "Think about what Python does when something requested cannot be found.",
            "hint2": "It raises a specific error named after keys.",
            "hint3": "It raises a `KeyError`. (Tip: You can use `prices.get('mango', 0)` to avoid crashing!)",
            "answer_keywords": ["keyerror", "key error", "error", "crashes", "crash", "exception"],
            "answer_explanation": "Spot on! Accessing an absent key with `[]` raises a `KeyError`. Using `.get('mango', default)` safely returns a fallback instead of crashing.",
            "challenge": "Create a dictionary with 3 student names as keys and their test scores as values, then calculate the average score."
        },
        "intermediate": {
            "concept": "**Hash Maps & O(1) Lookup**: Under the hood, a hash function converts keys into bucket array indices (`hash(key) % capacity`). Python dictionaries guarantee average O(1) insertion, deletion, and retrieval time.",
            "code": "from collections import defaultdict\n\n# Grouping words by length using a hash map\ngroups = defaultdict(list)\nfor word in ['cat', 'dog', 'tiger', 'lion']:\n    groups[len(word)].append(word)\nprint(dict(groups))  # {3: ['cat', 'dog'], 5: ['tiger'], 4: ['lion']}",
            "question": "What is a 'hash collision', and how does a hash table generally handle it?",
            "hint1": "Consider what happens if two completely different keys produce the exact same bucket index.",
            "hint2": "Think about techniques like chaining (linked lists) or open addressing (probing for the next open slot).",
            "hint3": "A collision occurs when two distinct keys yield identical hash buckets. Runtimes resolve it via open addressing (probing) or separate chaining.",
            "answer_keywords": ["collision", "same hash", "chaining", "open addressing", "probing", "same index", "same bucket"],
            "answer_explanation": "Exactly right! A collision occurs when two distinct keys hash to the same bucket index, resolved through open addressing (probing) or chaining.",
            "challenge": "Solve the classic 'Two Sum' problem: given a list of numbers and a target, find indices of the two numbers that sum to the target in O(N) time using a dictionary."
        },
        "advanced": {
            "concept": "**Internal Architecture & Compact Dicts**: Since Python 3.6+, dictionaries use a compact layout: a sparse hash index array pointing to a dense array of `(hash, key, value)`. This slashed memory by 30-40% while preserving insertion order.",
            "code": "# Requirements for dictionary keys:\n# Keys must be hashable: implement __hash__() and __eq__()\nclass Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __hash__(self):\n        return hash((self.x, self.y))\n    def __eq__(self, other):\n        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)",
            "question": "What causes worst-case O(N) degradation in a hash map, and how do modern security-minded runtimes mitigate HashDoS attacks?",
            "hint1": "Think about adversarial input crafted to target the exact same bucket.",
            "hint2": "Consider what happens if an attacker knows the hash algorithm and feeds thousands of colliding keys.",
            "hint3": "Runtimes randomize hash seeds per process (`PYTHONHASHSEED`) so attackers cannot predict collision sequences.",
            "answer_keywords": ["hashdos", "random seed", "seed", "collisions", "o(n)", "adversarial", "salt"],
            "answer_explanation": "Superb! Adversarial collisions force linear bucket scanning O(N). Runtimes randomize the hash seed per process on startup (`SipHash`) to thwart HashDoS attacks.",
            "challenge": "Implement an LRU (Least Recently Used) Cache class using an OrderedDict or a Hash Map combined with a Doubly Linked List in O(1) get and put."
        }
    },
    "functions": {
        "title": "Functions (Modularity & Scope)",
        "keywords": ["function", "functions", "def ", "parameter", "argument", "scope", "return"],
        "beginner": {
            "concept": "A **function** is a reusable machine in your code. You give it inputs (parameters), it does work, and it gives you back an output (return value). It saves you from writing the same code twice!",
            "code": "def greet(name):\n    return f'Welcome to coding, {name}! 🎉'\n\nmessage = greet('Alex')\nprint(message)",
            "question": "What is the difference between `print()` inside a function and `return`?",
            "hint1": "Think about what happens if you assign the function call to a variable: `result = my_func()`.",
            "hint2": "`print()` only displays text on the screen for humans to see.",
            "hint3": "`return` sends the calculated data back into your code so other functions and variables can use it.",
            "answer_keywords": ["return sends", "print only displays", "screen", "reuse", "value", "console", "variable"],
            "answer_explanation": "Great job! `print()` merely outputs text to the screen, while `return` passes data back so your program can store, manipulate, or reuse it.",
            "challenge": "Write a function `calculate_total(price, tax_rate)` that returns the total price after tax."
        },
        "intermediate": {
            "concept": "**First-Class Functions & Closures**: In Python and JavaScript, functions are first-class citizens. They can be passed as arguments, assigned to variables, and returned from other functions, retaining enclosing scope (closures).",
            "code": "def make_multiplier(factor):\n    # Inner function retains 'factor' via closure\n    def multiply(x):\n        return x * factor\n    return multiply\n\ndouble = make_multiplier(2)\nprint(double(5))  # Output: 10",
            "question": "What is the LEGB rule for variable scope resolution in Python?",
            "hint1": "It's an acronym for the 4 levels of scope searched sequentially.",
            "hint2": "L = Local, E = Enclosing...",
            "hint3": "L = Local, E = Enclosing (closures), G = Global, B = Built-in.",
            "answer_keywords": ["local enclosing global built-in", "local enclosing global builtin", "legb"],
            "answer_explanation": "Spot on! Python searches identifiers using **LEGB**: Local -> Enclosing (parent functions) -> Global (module level) -> Built-in.",
            "challenge": "Write a decorator `@timing_decorator` that measures and prints how many milliseconds a function takes to run."
        },
        "advanced": {
            "concept": "**Function Execution Frames & Inspection**: Functions are compiled into code objects (`func.__code__`) containing bytecode, variable names (`co_varnames`), and constants (`co_consts`). Inspection tools (`inspect`, `dis`) enable metaprogramming and dynamic dispatch.",
            "code": "import dis\ndef add(a, b):\n    return a + b\n# Disassemble into raw CPython bytecode\ndis.dis(add)",
            "question": "Why does using mutable default arguments like `def append_to(item, target=[])` create notorious bugs across calls?",
            "hint1": "When is the default argument expression evaluated: at function definition time, or each time the function is called?",
            "hint2": "Default arguments are evaluated once when the module loads, meaning `target` points to the same single list in memory!",
            "hint3": "Because the default list object is shared across all calls, subsequent invocations mutate that same object. (Fix: use `target=None`).",
            "answer_keywords": ["shared", "evaluated once", "definition time", "mutable", "same list", "same object"],
            "answer_explanation": "Exactly right! Default parameter expressions evaluate once at function definition time, binding a single shared mutable object across all subsequent calls.",
            "challenge": "Create a function signature validator decorator that inspects type hints at runtime and raises `TypeError` on invalid arguments."
        }
    },
    "lists": {
        "title": "Lists & Arrays (Sequences & Indexing)",
        "keywords": ["list", "lists", "array", "arrays", "indexing", "slicing", "append"],
        "beginner": {
            "concept": "A **List (or Array)** is an ordered shopping cart of items. Every item has an address number called an **Index**, and computers always start counting indices from **0**!",
            "code": "fruits = ['apple', 'banana', 'cherry']\n\n# Accessing the first item (index 0)\nprint(fruits[0])   # 'apple'\n\n# Adding a new item to the end\nfruits.append('mango')\nprint(fruits)      # ['apple', 'banana', 'cherry', 'mango']",
            "question": "In a list of 4 items, what is the index of the very last item?",
            "hint1": "Remember that the first item is at index 0.",
            "hint2": "Count them: item 1 is at 0, item 2 is at 1, item 3 is at 2...",
            "hint3": "The last item in a 4-item list is at index 3 (or `-1` in Python).",
            "answer_keywords": ["3", "index 3", "-1"],
            "answer_explanation": "Spot on! Because counting starts at 0, the last index of an N-element list is always `N - 1` (or `-1`).",
            "challenge": "Write code that reverses a list of numbers without using the built-in `.reverse()` method."
        },
        "intermediate": {
            "concept": "**Dynamic Array Growth Mechanics**: Python lists are dynamic contiguous arrays of pointers. When capacity is exceeded, Python over-allocates extra slots according to an amortized growth pattern (~1.125x) to guarantee O(1) amortized `append()`.",
            "code": "numbers = [1, 2, 3, 4, 5, 6]\n\n# Slice syntax: [start:stop:step]\nevens = numbers[1::2]   # [2, 4, 6]\nreversed_list = numbers[::-1]  # [6, 5, 4, 3, 2, 1]",
            "question": "Why is `list.append(x)` O(1) amortized, but `list.insert(0, x)` is O(N) time complexity?",
            "hint1": "Think about how items sit next to each other in contiguous memory.",
            "hint2": "Inserting at index 0 requires making room for the new element.",
            "hint3": "Every existing element in the array must shift one slot to the right, requiring N operations.",
            "answer_keywords": ["shift", "shifting", "move elements", "contiguous", "o(n) shift"],
            "answer_explanation": "Exactly! Inserting at index 0 forces every subsequent element to shift right by one index, taking O(N) time. Use `collections.deque` for O(1) front operations.",
            "challenge": "Implement a function that rotates a list to the right by `k` steps with O(1) auxiliary space."
        },
        "advanced": {
            "concept": "**Memory Architecture & Pointer Arrays**: A Python list does not store raw values inline; it stores contiguous 64-bit memory addresses (pointers to `PyObject` structs). This incurs pointer indirection and cache overhead compared to NumPy C-style contiguous buffers.",
            "code": "import sys\narr = []\n# Inspect internal memory allocation growth\nfor i in range(10):\n    arr.append(i)\n    print(f'Length: {len(arr)}, Allocated Bytes: {sys.getsizeof(arr)}')",
            "question": "What is the memory and performance advantage of `array.array` or NumPy arrays over standard Python lists for numeric data?",
            "hint1": "Compare storing pointers to Python integer objects vs storing raw bytes.",
            "hint2": "Python integers are full heap objects with reference counts and type info (28 bytes each).",
            "hint3": "NumPy/array buffers store unboxed raw C data types contiguously, eliminating pointer chasing and enabling SIMD vectorization.",
            "answer_keywords": ["unboxed", "pointer chasing", "simd", "contiguous memory", "raw bytes", "overhead", "cache"],
            "answer_explanation": "Spot on! Standard lists store boxed `PyObject*` pointers with heavy memory overhead. Typed contiguous buffers eliminate indirection and unlock SIMD CPU vectorization.",
            "challenge": "Write a vectorized dot-product calculation comparing pure Python lists against NumPy, measuring both execution time and memory footprint."
        }
    },
    "oop": {
        "title": "Object-Oriented Programming (Classes & Objects)",
        "keywords": ["oop", "class", "classes", "object", "inheritance", "self", "constructor"],
        "beginner": {
            "concept": "**Object-Oriented Programming (OOP)** is like creating a blueprint for real-world things. A **Class** is the blueprint (e.g. 'Car'), and an **Object** is an actual car built from that blueprint!",
            "code": "class Dog:\n    def __init__(self, name, breed):\n        self.name = name    # Attribute\n        self.breed = breed\n\n    def bark(self):         # Method (action)\n        return f'{self.name} says Woof! 🐶'\n\nmy_dog = Dog('Buddy', 'Golden Retriever')\nprint(my_dog.bark())",
            "question": "What does the `self` keyword represent inside a class method?",
            "hint1": "Think about how the computer knows which specific dog is barking.",
            "hint2": "`self` refers to the specific instance of the class that called the method.",
            "hint3": "`self` represents the specific object instance currently executing the code.",
            "answer_keywords": ["instance", "specific object", "current object", "itself", "the object"],
            "answer_explanation": "Spot on! `self` refers to the specific instance of the class calling the method, allowing each object to have its own unique attributes.",
            "challenge": "Create a `BankAccount` class with `balance`, and methods for `deposit(amount)` and `withdraw(amount)`."
        },
        "intermediate": {
            "concept": "**Inheritance & Polymorphism**: Subclasses inherit behavior from parent classes while overriding specific methods. Polymorphism lets you treat different classes with a shared interface uniformly.",
            "code": "class Animal:\n    def speak(self):\n        raise NotImplementedError\n\nclass Cat(Animal):\n    def speak(self):\n        return 'Meow! 🐱'\n\nclass Duck(Animal):\n    def speak(self):\n        return 'Quack! 🦆'\n\n# Polymorphic dispatch\nfor animal in [Cat(), Duck()]:\n    print(animal.speak())",
            "question": "What is the Purpose of `super().__init__()` in a child class constructor?",
            "hint1": "Think about what would happen to parent attributes if the child overrides `__init__`.",
            "hint2": "It invokes the parent class constructor so the parent's setup logic executes.",
            "hint3": "It initializes the inherited attributes defined in the parent class.",
            "answer_keywords": ["parent constructor", "parent class", "initialize parent", "super class", "base class"],
            "answer_explanation": "Exactly right! `super().__init__()` calls the parent class constructor, ensuring inherited state and validation are properly initialized.",
            "challenge": "Design an inheritance hierarchy with a base `Shape` class (`area()` and `perimeter()`) and `Rectangle` and `Circle` child classes."
        },
        "advanced": {
            "concept": "**MRO (Method Resolution Order) & Metaclasses**: In multiple inheritance, Python resolves method conflicts using the C3 Linearization algorithm (`Class.__mro__`). Metaclasses (`type`) control how classes themselves are constructed at import time.",
            "code": "class Meta(type):\n    def __new__(cls, name, bases, dct):\n        # Enforce all class methods must have docstrings\n        for k, v in dct.items():\n            if callable(v) and not v.__doc__:\n                raise TypeError(f'Method {k} requires a docstring!')\n        return super().__new__(cls, name, bases, dct)",
            "question": "What problem does Python's `__slots__` resolve in high-throughput object-heavy architectures?",
            "hint1": "Look into where Python ordinarily stores instance attributes for every object.",
            "hint2": "Normally, each object creates its own internal `__dict__` hash map to store attributes.",
            "hint3": "`__slots__` prevents the creation of `__dict__`, storing attributes in fixed-size C structs and saving up to 40-50% memory per instance.",
            "answer_keywords": ["__dict__", "dict", "memory", "slots", "faster", "attribute lookup", "ram"],
            "answer_explanation": "Superb! Standard Python objects allocate an internal `__dict__` hash table for attributes. `__slots__` allocates compact fixed-size arrays, drastically slashing memory overhead for millions of instances.",
            "challenge": "Implement a descriptor class that enforces runtime type validation on class attributes using `__get__` and `__set__`."
        }
    },
    "indentation": {
        "title": "Indentation & Code Blocks",
        "keywords": ["indent", "indentation", "indenting", "whitespace", "spaces", "tab ", "tabs", "taberror", "indentationerror"],
        "beginner": {
            "concept": "In Python, **indentation** (the spaces at the start of a line) tells the computer which lines belong together inside a block (like inside a function, `if` statement, or loop). Unlike languages that use curly braces `{}`, Python uses whitespace—standard practice is **4 spaces** per indentation level!",
            "code": "def check_temperature(temp):\n    # 4 spaces: inside the function\n    if temp > 25:\n        # 8 spaces: inside the if block!\n        print('It is warm! Wear shorts.')\n    else:\n        # 8 spaces: inside the else block!\n        print('It is cool! Grab a jacket.')\n    print('Temperature check complete.')  # back to 4 spaces\n\ncheck_temperature(30)",
            "question": "What happens in Python if you forget to indent the line directly under an `if` statement or function definition?",
            "hint1": "Python won't be able to tell what code belongs inside the statement.",
            "hint2": "The error name literally has the word 'indent' in it!",
            "hint3": "Python raises an `IndentationError: expected an indented block` and halts execution.",
            "answer_keywords": ["indentationerror", "indentation error", "expected an indented block", "syntax error", "error"],
            "answer_explanation": "Exactly! Python raises an `IndentationError: expected an indented block`. Because Python does not use curly brackets, consistent indentation is mandatory syntax.",
            "challenge": "Write an if-else statement checking if `score >= 50`, properly indenting the pass/fail print statements with 4 spaces."
        },
        "intermediate": {
            "concept": "**Tabs vs. Spaces & Lexical Tokenization**: Python strictly forbids mixing tabs and spaces (`TabError: inconsistent use of tabs and spaces`). PEP 8 standardizes on exactly 4 spaces. The Python compiler tokenizes source code by generating `INDENT` and `DEDENT` tokens whenever whitespace depth shifts.",
            "code": "# PEP 8 Standard: 4 spaces per nesting level\nnumbers = [1, 2, 3, 4]\nfor n in numbers:           # 0 spaces\n    if n % 2 == 0:          # 4 spaces (Level 1)\n        print(f'{n} is even')  # 8 spaces (Level 2)\n    else:\n        print(f'{n} is odd')   # 8 spaces (Level 2)",
            "question": "Why is mixing tabs and spaces dangerous in collaborative teams, and how does `TabError` occur?",
            "hint1": "Think about how different code editors display tab characters.",
            "hint2": "One developer's editor might show a tab as 2 spaces, while another editor renders it as 8 spaces.",
            "hint3": "Because tab visual widths vary, code can look aligned to a human while having mismatched ASCII characters, triggering Python's `TabError`.",
            "answer_keywords": ["taberror", "inconsistent", "pep 8", "editor width", "different editors", "visual", "tabs and spaces"],
            "answer_explanation": "Spot on! Different editors interpret tabs with varying column widths. Code that visually aligns on one screen may trigger `TabError` or logical scope bugs on another. Linters (Black, Ruff) enforce 4 spaces.",
            "challenge": "Write a Python function `check_indentation_spaces(file_path)` that inspects lines and returns line numbers that contain raw tab characters `\\t`."
        },
        "advanced": {
            "concept": "**The Off-side Rule & CPython Parser**: Python implements Peter Landin's *off-side rule*, where visual whitespace depth dictates Abstract Syntax Tree (AST) hierarchy. CPython's tokenizer (`Parser/lexer/lexer.c`) maintains an explicit indentation stack (`indent_stack`), generating `INDENT` when whitespace increases and `DEDENT` tokens when it decreases. Inside parentheses `()`, brackets `[]`, or braces `{}`, whitespace tokenization is suppressed via implicit line continuation.",
            "code": "import tokenize\nimport io\n\nsource = '''if True:\n    x = 42\n'''\n\ntokens = tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline)\nfor tok in tokens:\n    if tok.type in (tokenize.INDENT, tokenize.DEDENT):\n        print(f'Token: {tokenize.tok_name[tok.type]} at line {tok.start[0]}')",
            "question": "How does CPython's tokenizer handle implicit line continuations within parentheses `()`, and why don't they push new entries onto the indentation stack?",
            "hint1": "Think about multi-line list literals or function signatures.",
            "hint2": "Does Python force you to indent by exactly 4 spaces when wrapping a multi-line list inside brackets?",
            "hint3": "The tokenizer increments a delimiter nesting level (`parenlevel`). When `parenlevel > 0`, newline characters emit `NL` instead of `NEWLINE`, so the indentation stack is completely bypassed.",
            "answer_keywords": ["parenlevel", "implicit", "continuation", "nl token", "nesting", "parentheses", "bracket"],
            "answer_explanation": "Brilliant! CPython tracks delimiter depth (`parenlevel`). When `parenlevel > 0`, newlines generate `NL` instead of statement `NEWLINE` tokens, bypassing indentation depth verification completely.",
            "challenge": "Use Python's `tokenize` module to inspect a multi-line code string containing nested parentheses and verify that `NL` tokens are emitted instead of `NEWLINE`/`INDENT`."
        }
    }
}

class TutorEngine:
    def __init__(self):
        pass

    def chat(self, req: ChatRequest) -> ChatResponse:
        """
        Conversational programming tutor adhering strictly to pedagogical principles:
        1. Simple concept explanation
        2. Clean code snippet
        3. Related check question (Your Turn)
        4. Progressive hints (Hint 1 -> Hint 2 -> Hint 3) when stuck
        5. Never spoils the answer when a hint can help
        6. Ends with a quick practice challenge
        """
        # Attempt OpenAI LLM if configured in .env
        openai_reply = self._call_openai_tutor(req)
        if openai_reply:
            return openai_reply

        # Fallback to intelligent built-in pedagogical tutor engine
        return self._builtin_tutor(req)

    def _get_llm_clients(self):
        """Yields available (client, model_name, provider) tuples in order of priority."""
        from dotenv import load_dotenv
        load_dotenv(override=True)

        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        from openai import OpenAI

        # 1. Gemini with high-availability model cascading
        if gemini_key:
            client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            # Cycle through available Gemini models to guarantee high availability and prevent 429 quota blockages
            gemini_models = [
                os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip(),
                "gemini-flash-lite-latest",
                "gemini-3.7-flash",
                "gemini-3.5-flash-lite",
                "gemini-flash-latest",
                "gemini-3.5-flash",
                "gemini-3.6-flash"
            ]
            seen = set()
            for m in gemini_models:
                if m and m not in seen:
                    seen.add(m)
                    yield client, m, f"Gemini ({m})"

        # 2. OpenAI fallback
        if openai_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
            yield OpenAI(api_key=openai_key), model, "OpenAI"

    def _get_llm_client(self):
        """Returns the first available LLM client."""
        for client, model, provider in self._get_llm_clients():
            return client, model, provider
        return None, None, None

    @staticmethod
    def _sanitize_output(text: str) -> str:
        if not text:
            return ""
        # Clean LaTeX math syntax and arrows
        replacements = [
            (r"$\rightarrow$", "→"),
            (r"$\leftarrow$", "←"),
            (r"\rightarrow", "→"),
            (r"\leftarrow", "←"),
            (r"$\to$", "→"),
            (r"\to", "→"),
            (r"\times", "×"),
            (r"\cdot", "·"),
            (r"\approx", "≈"),
            (r"\le", "≤"),
            (r"\ge", "≥"),
            (r"\ne", "≠"),
            (r"\log", "log"),
            (r"\ln", "ln"),
            (r"\lg", "lg"),
            (r"\sqrt", "√"),
            (r"\infty", "∞"),
            (r"\sum", "∑"),
            (r"\prod", "∏"),
            (r"\pm", "±"),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        # Remove raw dollar wrappers $N$ -> N
        text = re.sub(r"\$([^$\n]+)\$", r"\1", text)
        return text

    def _call_openai_tutor(self, req: ChatRequest) -> Optional[ChatResponse]:
        mode = getattr(req, "mode", "learn") or "learn"

        mode_prompts = {
            "learn": """PRIMARY MODE: LEARN CONCEPT
You teach programming concepts clearly, directly, and step-by-step with high technical precision and clean practical code.
Follow this mandatory structure:
### 💡 Concept: [Topic Name]
[Provide a clear, direct, 2-3 sentence technical definition. Explain what the concept is, how it operates in execution flow or memory, and why it is used. Focus on genuine programming mechanics rather than child-like analogies.]

### 💻 Code Example
```[language]
[Provide a clean, realistic, and well-commented code example directly demonstrating the concept.]
```

### 📌 Key Takeaways
- [Core takeaway 1: Syntax rule or execution behavior]
- [Core takeaway 2: Time / Space complexity or performance property]
- [Core takeaway 3: Practical best practice or common pitfall to avoid]

### ❓ Check Question
[Ask ONE precise check question (e.g. asking the student to predict the output of a short code snippet or analyze an edge case condition) to verify their understanding.]
""",
            "hint": """PRIMARY MODE: PROGRESSIVE HINT
The student is stuck or needs guidance.
- NEVER reveal the full code solution or direct answer immediately!
- If this is their first request for a hint, provide **💡 Hint 1: Conceptual Direction** (a gentle nudge).
- If they are still stuck, provide **💡 Hint 2: Structural Clue** (closer guidance).
- If they need more help, provide **💡 Hint 3: Key Logic Clue**.
- End with an encouraging guiding question.
""",
            "challenge": """PRIMARY MODE: CODING CHALLENGE
- If the student is asking for a challenge or new problem:
  ### 🎯 Challenge: [Problem Title]
  **Problem Statement**: [Clear, engaging problem description]
  **Example Input & Output**:
  - `Input: ...` -> `Output: ...`
  **Your Task**: Write the code/logic to solve this. Send your attempt!
- If the student submitted a solution attempt:
  - Evaluate correctness, edge cases, and time/space complexity.
  - Highlight what they did well and offer friendly suggestions.
""",
            "quiz": """PRIMARY MODE: QUIZ ME
- Ask EXACTLY ONE multiple-choice or short-answer question at a time.
- If the student just answered your previous question:
  1. Clearly state if they are **Correct! 🎉** or **Not quite right 🤔**.
  2. Explain the reason why in 1-2 friendly sentences.
  3. Then present the **Next Question** with options A, B, C, D.
- If this is the start of a quiz, present Question 1 immediately with clean code snippet and options A, B, C, D.
""",
            "review": """PRIMARY MODE: CODE REVIEW
- Review the student's code thoroughly for:
  1. Syntax & logic correctness
  2. Time & space complexity
  3. Clean code practices and readability
- Provide specific, encouraging before/after code snippets.
""",
            "chat": """PRIMARY MODE: GENERAL PROGRAMMING TUTOR
- Answer the student's programming question with direct clarity, practical code examples, and structured guidance.
- Always include an interactive follow-up question.
"""
        }

        system_instruction = f"""You are CodeTutor AI, a master computer science educator and programming tutor.
You provide direct, structured, high-quality programming instruction with crystal-clear definitions, realistic code snippets, and sharp conceptual check questions.

{mode_prompts.get(mode, mode_prompts['learn'])}

CORE PEDAGOGICAL & QUALITY GUIDELINES:
1. DIRECT & PROFESSIONAL EXPLANATIONS: Provide precise, clear technical definitions of how code works, memory behaves, and algorithms execute. Avoid conversational filler or childish analogies.
2. ACCURATE & RELEVANT EXAMPLES: Write clean, modern, and practical code snippets in the requested language (Python, C, C++, Java, JS, etc.) with helpful comments.
3. 100% COMPLETE CODE: Always provide complete, runnable code inside ```language ... ``` fences without placeholders or truncation.
4. SHARP CHECK QUESTIONS: Always end with a thought-provoking check question (e.g. predicting output, edge-case analysis) so the student actively learns.
5. NO RAW LATEX OR ARTIFACTS: Use clean Unicode symbols (→, ←, ≤, ≥, ≠, ×, √) and clean formatting.
"""

        messages = [{"role": "system", "content": system_instruction}]
        for m in req.history[-10:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": req.message})

        for client, model, provider in self._get_llm_clients():
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.6,
                    max_tokens=2500
                )

                reply_text = completion.choices[0].message.content or ""
                
                if mode == "learn":
                    followups = [
                        "💡 I'm stuck, give me a Hint",
                        "🎯 Give me a Challenge on this",
                        "❓ Quiz me on this topic",
                        "Show another code example"
                    ]
                elif mode == "hint":
                    followups = [
                        "💡 Give me Hint 2",
                        "💡 Give me Hint 3 (Final Clue)",
                        "I think the answer is...",
                        "Explain the concept again"
                    ]
                elif mode == "challenge":
                    followups = [
                        "Here is my solution attempt...",
                        "💡 I need a hint for this challenge",
                        "Give me another challenge",
                        "Explain the optimal solution"
                    ]
                elif mode == "quiz":
                    followups = [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ]
                elif mode == "review":
                    followups = [
                        "How can I optimize this?",
                        "Check edge cases",
                        "Is there a cleaner way to write this?"
                    ]
                else:
                    followups = [
                        "💡 Explain with an example",
                        "🎯 Give me a challenge",
                        "❓ Quiz me on this",
                        "How does this work under the hood?"
                    ]

                return ChatResponse(
                    reply=self._sanitize_output(reply_text),
                    mode=mode,
                    difficulty=req.difficulty,
                    suggested_followups=followups
                )
            except Exception as e:
                print(f"[CodeTutor AI] LLM ({provider}) note: {e}. Trying next provider...")

        return None

    def _builtin_tutor(self, req: ChatRequest) -> ChatResponse:
        """Rule-based pedagogical engine providing full 6-step tutoring with 3 progressive hints."""
        msg = req.message.strip()
        msg_lower = msg.lower()
        level = req.difficulty

        # 1. Check if student is asking for a hint or says they are stuck
        is_hint_requested = bool(re.search(r"\b(hint|stuck|don't know|dont know|help|clue|no idea|confused|give up|lost|answer please)\b", msg_lower))

        # 2. Greetings (ensure word boundaries so 'hi' doesn't match 'hint')
        is_greeting = bool(re.search(r"\b(hello|hi|hey|good morning|good evening|howdy)\b", msg_lower)) and len(msg.split()) <= 4
        if is_greeting and not is_hint_requested:
            return ChatResponse(
                reply=(
                    f"👋 Hello! I'm **CodeTutor AI**, your dedicated programming tutor calibrated for **{level.capitalize()}** learners.\n\n"
                    f"Unlike ordinary chatbots that just paste entire solutions, I work with you step-by-step:\n"
                    f"1. 💡 **Explain concepts** simply with intuitive analogies.\n"
                    f"2. 💻 **Provide clean, focused code examples**.\n"
                    f"3. ❓ **Ask check questions** to verify your understanding.\n"
                    f"4. 💡 **Provide 3 progressive hints** if you ever get stuck (without spoiling the answer!).\n"
                    f"5. 🎯 **Give quick practice challenges** so you learn by doing.\n\n"
                    f"What programming concept would you like to explore today?"
                ),
                difficulty=level,
                suggested_followups=[
                    "How do loops work?",
                    "Explain recursion simply",
                    "What is a Hash Map / Dictionary?",
                    "How do functions work?"
                ]
            )

        # 3. Identify active topic
        topic_key = self._detect_topic(msg_lower, req.history)
        topic_info = TUTOR_TOPICS.get(topic_key)
        tier_data = topic_info.get(level) if topic_info else None

        if is_hint_requested and tier_data:
            # Count previous hints given in history for this topic
            hint_count = self._count_previous_hints(req.history)
            
            # Explicit hint number requested?
            if "hint 1" in msg_lower or hint_count == 0:
                return ChatResponse(
                    reply=(
                        f"### 💡 Hint 1: A Gentle Nudge\n\n"
                        f"{tier_data['hint1']}\n\n"
                        f"> 🤝 **Tutor Rule**: *I won't give away the solution just yet because solving it yourself is how programming truly clicks! Take this clue and give it another thought.*"
                    ),
                    difficulty=level,
                    suggested_followups=[
                        "💡 I'm still stuck, give me Hint 2",
                        "I think the answer is...",
                        "Can you rephrase the question?"
                    ]
                )
            elif "hint 2" in msg_lower or hint_count == 1:
                return ChatResponse(
                    reply=(
                        f"### 💡 Hint 2: A Closer Structural Clue\n\n"
                        f"{tier_data['hint2']}\n\n"
                        f"> 🔍 **You're getting warmer!** *Think about how this connects to the code example. What is your hypothesis?*"
                    ),
                    difficulty=level,
                    suggested_followups=[
                        "💡 Give me Hint 3 (Final Clue)",
                        "Here is my attempt...",
                        "Can you explain the previous hint?"
                    ]
                )
            elif "hint 3" in msg_lower or hint_count == 2:
                return ChatResponse(
                    reply=(
                        f"### 💡 Hint 3: The Final Clue\n\n"
                        f"{tier_data['hint3']}\n\n"
                        f"> 🎯 **Almost there!** *This is the last piece of the puzzle. Put it together—what do you think?*"
                    ),
                    difficulty=level,
                    suggested_followups=[
                        "Reveal the full answer & explanation",
                        "Here is my final answer!"
                    ]
                )
            else:
                # 3 hints already given, reveal solution and challenge
                return ChatResponse(
                    reply=(
                        f"### 🏆 Answer & Explanation\n\n"
                        f"{tier_data['answer_explanation']}\n\n"
                        f"Outstanding persistence working through all the clues! Ready to put it into practice?\n\n"
                        f"---\n\n"
                        f"### 🎯 Quick Practice Challenge:\n"
                        f"{tier_data['challenge']}"
                    ),
                    difficulty=level,
                    suggested_followups=[
                        "Can we explore another concept?",
                        "Give me another practice challenge",
                        f"Switch to {'intermediate' if level == 'beginner' else 'advanced'} mode"
                    ]
                )

        # 4. Check if student is answering the check question
        if tier_data and self._matches_answer(msg_lower, tier_data.get("answer_keywords", [])):
            return ChatResponse(
                reply=(
                    f"🎉 **Spot on! That is exactly right!**\n\n"
                    f"{tier_data['answer_explanation']}\n\n"
                    f"---\n\n"
                    f"### 🎯 Next Step: Quick Practice Challenge\n"
                    f"{tier_data['challenge']}\n\n"
                    f"Try writing the solution or paste your code here when you're ready!"
                ),
                difficulty=level,
                suggested_followups=[
                    "I'm ready for another topic!",
                    "Can you give me a hint for the challenge?",
                    f"Explain {topic_info['title']} at an advanced level"
                ]
            )

        # 5. Full pedagogical tutor response for a known topic
        if tier_data:
            return ChatResponse(
                reply=(
                    f"### 💡 Concept: {topic_info['title']}\n"
                    f"{tier_data['concept']}\n\n"
                    f"### 💻 Code Example:\n"
                    f"```python\n{tier_data['code']}\n```\n\n"
                    f"### ❓ Your Turn:\n"
                    f"{tier_data['question']}\n\n"
                    f"---\n\n"
                    f"### 🎯 Quick Practice Challenge:\n"
                    f"{tier_data['challenge']}"
                ),
                difficulty=level,
                suggested_followups=[
                    "💡 I'm stuck, need Hint 1",
                    "I think the answer is...",
                    "Can you show an example in JavaScript?",
                    "Give me an easier example"
                ]
            )

        # 6. Intelligent adaptive response that actually addresses the user's question
        return self._smart_fallback(msg, level)

    def _smart_fallback(self, msg: str, level: str) -> ChatResponse:
        """
        Context-aware fallback that actually addresses the user's specific question
        instead of returning a generic unrelated demo every time.
        """
        # Extract a clean concept label from the user's message
        # Remove common filler words and keep the most meaningful part
        filler = {
            "what", "how", "is", "are", "does", "do", "the", "a", "an",
            "explain", "tell", "me", "about", "can", "you", "work", "works",
            "i", "in", "python", "please", "understand", "help", "with",
            "want", "to", "know", "concept", "of", "give", "example", "simple"
        }
        words = re.findall(r"[a-zA-Z0-9_]+", msg.lower())
        topic_words = [w for w in words if w not in filler and len(w) > 2]
        concept = " ".join(topic_words[:4]).title() if topic_words else "Programming Concepts"

        # Build a level-appropriate code example relevant to what was asked
        if level == "beginner":
            complexity_note = "Keep it simple — clear variable names and short functions."
            code_stub = (
                f"# {concept} — beginner example\n"
                f"def solve_problem(input_value):\n"
                f"    # Step 1: understand the input\n"
                f"    print(f'Input: {{input_value}}')\n"
                f"    # Step 2: apply logic\n"
                f"    result = input_value  # replace with actual logic\n"
                f"    return result\n\n"
                f"print(solve_problem('your value here'))"
            )
            check_q = (
                f"What would happen if you called `solve_problem(42)`? "
                f"Try tracing through the code step by step."
            )
            challenge = (
                f"Rewrite `solve_problem` so it doubles any number input. "
                f"Test it with 3, 7, and 100."
            )
        elif level == "intermediate":
            complexity_note = "Think about edge cases, time complexity, and reusability."
            code_stub = (
                f"# {concept} — intermediate example\n"
                f"from typing import Any, List\n\n"
                f"def process(data: List[Any]) -> List[Any]:\n"
                f"    \"\"\"Applies a transformation relevant to {concept}.\"\"\"\n"
                f"    if not data:\n"
                f"        return []  # edge case: empty input\n"
                f"    return [item for item in data if item is not None]  # adapt to your logic\n\n"
                f"print(process([1, None, 3, None, 5]))"
            )
            check_q = (
                f"What is the time complexity of `process()` above, and "
                f"can you think of a scenario where a different data structure "
                f"would make it more efficient?"
            )
            challenge = (
                f"Extend `process` to also accept a `transform` function parameter "
                f"and apply it to each non-None element in a single pass."
            )
        else:  # advanced
            complexity_note = "Consider memory layout, concurrency implications, and Big-O analysis."
            code_stub = (
                f"# {concept} — advanced example\n"
                f"from functools import reduce\n"
                f"from typing import Callable, Iterator, TypeVar\n\n"
                f"T = TypeVar('T')\n\n"
                f"def pipeline(*funcs: Callable) -> Callable:\n"
                f"    \"\"\"Compose multiple transformations into a single callable pipeline.\"\"\"\n"
                f"    return reduce(lambda f, g: lambda x: g(f(x)), funcs)\n\n"
                f"# Example: double → square → negate\n"
                f"transform = pipeline(lambda x: x * 2, lambda x: x ** 2, lambda x: -x)\n"
                f"print(transform(3))  # -((3*2)^2) = -36"
            )
            check_q = (
                f"Why does `reduce` compose functions right-to-left vs. left-to-right, "
                f"and how would you reverse the composition order without changing the pipeline call?"
            )
            challenge = (
                f"Implement a lazy evaluation version of `pipeline` using generator expressions "
                f"so transformations only execute when the final result is consumed."
            )

        available_topics = [info["title"] for info in TUTOR_TOPICS.values()]
        topic_suggestions = available_topics[:4]

        return ChatResponse(
            reply=(
                f"### 💡 Let's Explore: **{concept}**\n\n"
                f"> 📚 I don't have a pre-built lesson for this exact topic yet, but here is a "
                f"**{level.capitalize()}-level** walkthrough tailored to your question!\n\n"
                f"**Key idea at {level} level**: {complexity_note}\n\n"
                f"### 💻 Code Example:\n"
                f"```python\n{code_stub}\n```\n\n"
                f"### ❓ Your Turn:\n"
                f"{check_q}\n\n"
                f"---\n\n"
                f"### 🎯 Quick Practice Challenge:\n"
                f"{challenge}\n\n"
                f"---\n\n"
                f"> 💬 **Tip**: For topics with full tutor support (concept → hints → answer), try asking about:\n"
                + "\n".join(f"> - {t}" for t in topic_suggestions)
            ),
            difficulty=level,
            suggested_followups=[
                "💡 I'm stuck, give me Hint 1",
                "Give me a simpler example",
                "How do loops work?",
                "Explain recursion",
                "What are dictionaries?"
            ]
        )

    def _detect_topic(self, text: str, history: List[Any]) -> Optional[str]:
        """Detect which programming topic is currently active."""
        # Normalize common typos
        normalized_text = text.lower()
        normalized_text = re.sub(r"\bexpalin\b", "explain", normalized_text)
        normalized_text = re.sub(r"\bexplan\b", "explain", normalized_text)
        normalized_text = re.sub(r"\bindentaion\b", "indentation", normalized_text)
        normalized_text = re.sub(r"\brecusion\b", "recursion", normalized_text)
        normalized_text = re.sub(r"\bvarible\b", "variable", normalized_text)
        normalized_text = re.sub(r"\bfuncton\b", "function", normalized_text)
        normalized_text = re.sub(r"\bdictinary\b", "dictionary", normalized_text)

        # 1. Check current message first
        for key, data in TUTOR_TOPICS.items():
            if any(kw in normalized_text for kw in data["keywords"]):
                return key

        # 2. ONLY check recent history if the student is asking for a hint or follow-up
        # If the user is asking a new question, NEVER latch onto the old topic from history!
        is_followup = bool(re.search(
            r"\b(hint|stuck|help|clue|no idea|confused|give up|lost|answer please|more|another|next|why|continue)\b",
            normalized_text
        ))
        if is_followup:
            for item in reversed(history[-4:]):
                content = getattr(item, "content", "").lower()
                for key, data in TUTOR_TOPICS.items():
                    if any(kw in content for kw in data["keywords"]):
                        return key

        return None

    def _count_previous_hints(self, history: List[Any]) -> int:
        """Count how many hints were dispensed in recent assistant messages."""
        count = 0
        for item in reversed(history[-6:]):
            role = getattr(item, "role", "")
            content = getattr(item, "content", "")
            if role == "assistant":
                if "💡 Hint 3" in content:
                    return 3
                elif "💡 Hint 2" in content:
                    return max(count, 2)
                elif "💡 Hint 1" in content:
                    count = max(count, 1)
        return count

    def _matches_answer(self, text: str, keywords: List[str]) -> bool:
        """Check if user answer matches expected keywords."""
        return any(kw in text for kw in keywords)


    def explain_code(self, req: ExplainRequest) -> ExplainResponse:
        """Break down a code snippet into structured line-by-line analysis, concepts, and complexity."""
        # 1. Try OpenAI if configured in .env
        openai_res = self._call_openai_explain(req)
        if openai_res:
            return openai_res

        # 2. Advanced built-in code analysis engine
        return self._builtin_explain(req)

    def _call_openai_explain(self, req: ExplainRequest) -> Optional[ExplainResponse]:
        """Use Gemini or OpenAI to analyze code with deep pedagogical insights."""
        import json

        prompt = f"""You are an elite computer science tutor and programming instructor.
Analyze the following code (which may be in ANY language, e.g. Python, C, C++, Java, JavaScript, Rust, Go, SQL, etc.).

CODE:
```
{req.code}
```

Return ONLY a valid JSON object matching this exact schema:
{{
  "language": "Detected language name (e.g. C, C++, Python, JavaScript, Java)",
  "summary": "2-3 clear sentences explaining what the code accomplishes and its primary algorithm/strategy.",
  "concepts": ["Concept 1", "Concept 2", "Concept 3"],
  "time_complexity": "e.g. O(log N) - binary search halving remaining space",
  "space_complexity": "e.g. O(1) - constant auxiliary memory",
  "tutor_tips": [
    "Practical, student-friendly tip 1",
    "Practical, student-friendly tip 2",
    "Practical, student-friendly tip 3"
  ],
  "line_by_line": [
    {{
      "line_number": 1,
      "code": "exact code on this line",
      "explanation": "Clear, student-friendly explanation of what this specific line does."
    }}
  ]
}}
"""

        for client, model, provider in self._get_llm_clients():
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                raw = completion.choices[0].message.content or "{}"
                data = json.loads(raw)

                lines_data = []
                for item in data.get("line_by_line", []):
                    lines_data.append(LineExplanation(
                        line_number=int(item.get("line_number", 1)),
                        code=str(item.get("code", "")),
                        explanation=str(item.get("explanation", ""))
                    ))

                detected_lang = data.get("language") or req.language or "Code"
                if not lines_data:
                    lines_data = self._builtin_line_by_line(req.code, detected_lang, req.difficulty)

                return ExplainResponse(
                    language=detected_lang,
                    difficulty=req.difficulty,
                    summary=data.get("summary", "Code analysis complete."),
                    line_by_line=lines_data,
                    concepts=data.get("concepts", ["Core Algorithm Flow"]),
                    time_complexity=data.get("time_complexity", "O(N)"),
                    space_complexity=data.get("space_complexity", "O(1)"),
                    tutor_tips=data.get("tutor_tips", ["Test with minimal edge case inputs."])
                )
            except Exception as e:
                print(f"[CodeTutor AI] LLM ({provider}) explain note: {e}. Trying next provider...")

        return None

    def _builtin_explain(self, req: ExplainRequest) -> ExplainResponse:
        """Deep, robust heuristic code analyzer supporting Python, JavaScript, and other languages."""
        code = req.code.strip()
        lang = req.language.lower()
        level = req.difficulty
        lines = code.split("\n")

        line_exps = self._builtin_line_by_line(code, lang, level)
        concepts: set[str] = set()

        # Concept detection
        for line in lines:
            line_str = line.strip()
            if "def " in line_str or "function " in line_str or "=>" in line_str:
                concepts.add("Function Modularity")
            if "for " in line_str or "while " in line_str:
                concepts.add("Iteration & Loops")
            if "if " in line_str or "elif " in line_str or "else" in line_str:
                concepts.add("Conditional Logic")
            if "return " in line_str:
                concepts.add("Return Values")
            if "[" in line_str and "]" in line_str:
                concepts.add("Array / List Indexing")
            if "{" in line_str and "}" in line_str and ":" in line_str:
                concepts.add("Hash Maps / Dictionaries")
            if "memo" in line_str or "cache" in line_str:
                concepts.add("Dynamic Programming (Memoization)")
            if ("left" in line_str and "right" in line_str) or ("mid" in line_str and "// 2" in line_str):
                concepts.add("Binary Search (Two Pointers)")
            if "class " in line_str:
                concepts.add("Object-Oriented Programming (Classes)")
            if "try:" in line_str or "catch" in line_str:
                concepts.add("Exception Handling")
            if "async " in line_str or "await " in line_str or "Promise" in line_str:
                concepts.add("Asynchronous Execution")

        # Fallback concepts
        if not concepts:
            concepts.add("Sequential Execution")
            concepts.add("Variable State Tracking")

        # Algorithmic Complexity Detection
        has_binary_search = ("left" in code and "right" in code) and ("// 2" in code or "Math.floor" in code or "binary" in code)
        loop_count = sum(1 for line in lines if any(k in line for k in ["for ", "while "]))

        if has_binary_search:
            time_comp = "O(log N)"
            time_reason = "Binary search divides the search space in half with every iteration."
            space_comp = "O(1)"
        elif "memo" in code and "fib" in code:
            time_comp = "O(N)"
            time_reason = "Memoization caches computed subproblems, eliminating exponential redundant work."
            space_comp = "O(N)"
        elif loop_count >= 2:
            time_comp = "O(N²)"
            time_reason = "Nested loops iterating over data, resulting in quadratic operation growth."
            space_comp = "O(N)" if any(k in code for k in ["[]", "list(", "dict(", "{}"]) else "O(1)"
        elif loop_count == 1:
            time_comp = "O(N)"
            time_reason = "Single pass through the collection, scaling linearly with input size."
            space_comp = "O(N)" if any(k in code for k in ["[]", "list(", "dict(", "{}"]) else "O(1)"
        else:
            time_comp = "O(1)"
            time_reason = "Constant-time instructions executing without loops or unbounded recursion."
            space_comp = "O(1)"

        # Tailored pedagogical summary
        if level == "beginner":
            summary = (
                f"This {lang.capitalize()} program executes step-by-step across {len(line_exps)} statements. "
                f"It utilizes {', '.join(list(concepts)[:3])} to solve its task clearly and predictably."
            )
            tips = [
                "Trace the variables step-by-step on paper or use print() statements to watch values update.",
                "Pay close attention to block indentation and loop terminating conditions.",
                "Always check how the code behaves with an empty input or single item."
            ]
        elif level == "intermediate":
            summary = (
                f"A structured {lang.capitalize()} implementation demonstrating {', '.join(list(concepts))}. "
                f"It achieves an estimated {time_comp} time complexity and {space_comp} auxiliary memory footprint."
            )
            tips = [
                "Consider edge cases: empty collections, duplicate elements, or negative numbers.",
                "Evaluate if memory can be saved with generators or in-place pointer mutations.",
                "Ensure meaningful type annotations and docstrings are present for team maintainability."
            ]
        else:
            summary = (
                f"Algorithmic evaluation: Operates within {time_comp} computational bounds ({time_reason}) "
                f"and {space_comp} auxiliary space overhead. Core design patterns identified: {', '.join(list(concepts))}."
            )
            tips = [
                "Analyze CPU cache line locality: contiguous array reads vs pointer chasing.",
                "Verify branch prediction impact inside tight inner loop conditions.",
                "Check reentrancy and thread safety if executed within concurrent environments."
            ]

        return ExplainResponse(
            language=lang,
            difficulty=level,
            summary=summary,
            line_by_line=line_exps,
            concepts=sorted(list(concepts)),
            time_complexity=time_comp,
            space_complexity=space_comp,
            tutor_tips=tips
        )

    def _builtin_line_by_line(self, code: str, lang: str, level: str) -> List[LineExplanation]:
        """Generate accurate line-by-line breakdown annotations."""
        lines = code.split("\n")
        line_exps: List[LineExplanation] = []

        for idx, raw_line in enumerate(lines, start=1):
            line_str = raw_line.strip()
            if not line_str:
                continue

            explanation = self._explain_single_line(line_str, lang, level)
            line_exps.append(LineExplanation(
                line_number=idx,
                code=raw_line,
                explanation=explanation
            ))
        return line_exps

    def _explain_single_line(self, line: str, lang: str, level: str) -> str:
        """Produce clear, student-friendly explanation for a single statement."""
        # Comments
        if line.startswith("#") or line.startswith("//"):
            return "Comment: Human-readable note explaining the purpose of the code below."

        # Function Declarations
        if line.startswith("def ") or line.startswith("function ") or "=>" in line:
            name_match = re.findall(r"(?:def|function)\s+([a-zA-Z0-9_]+)", line)
            func_name = name_match[0] if name_match else "function"
            return f"Declares reusable function `{func_name}` with its input parameters."

        # Returns
        if line.startswith("return ") or "return " in line:
            return "Exits the current function and passes the computed result back to the caller."

        # Binary search mid & pointers
        if "mid =" in line or "mid=" in line:
            return "Calculates midpoint index using integer division `// 2` to divide search range in half."
        if "left, right =" in line or "left = 0" in line or "let left = 0" in line:
            return "Initializes two pointer boundaries (start and end) for searching or scanning."
        if "left = mid + 1" in line or "left = mid+1" in line:
            return "Narrows search window to the right half by skipping elements smaller than target."
        if "right = mid - 1" in line or "right = mid-1" in line:
            return "Narrows search window to the left half by skipping elements larger than target."

        # Loops
        if line.startswith("while "):
            return "Starts a loop that repeatedly executes as long as the condition evaluates to True."
        if line.startswith("for ") and "in " in line:
            return "Loops through each element in the collection or range sequentially."

        # Conditionals
        if line.startswith("if "):
            return "Evaluates a condition; if True, executes the indented code block below."
        if line.startswith("elif ") or line.startswith("else if"):
            return "Secondary check evaluated only if preceding conditional branches were False."
        if line.startswith("else:"):
            return "Default fallback branch executed when none of the previous conditions matched."

        # Dictionary / Object memoization
        if "memo[" in line or "memo =" in line or "memo={}" in line:
            return "Stores or retrieves cached results in a lookup table (memoization) to eliminate redundant work."

        # Assignments
        if "=" in line and "==" not in line and "!=" not in line and "<=" not in line and ">=" not in line:
            var_name = line.split("=")[0].strip().replace("let ", "").replace("const ", "").replace("var ", "")
            return f"Computes value and assigns it to variable `{var_name}`."

        # Print / logs
        if line.startswith("print(") or line.startswith("console.log("):
            return "Outputs information to the console/terminal for inspection or debugging."

        # Push / append
        if "append(" in line or "push(" in line:
            return "Adds an element to the end of the collection in O(1) amortized time."

        return "Executes an operation or statement in the normal flow of the program."

    def debug_code(self, req: DebugRequest) -> DebugResponse:
        """Scan code for syntax & semantic bugs, explain the root cause, and provide fixed code."""
        # 1. Try OpenAI if configured
        openai_res = self._call_openai_debug(req)
        if openai_res:
            return openai_res

        # 2. Comprehensive built-in bug diagnostics
        return self._builtin_debug(req)

    def _call_openai_debug(self, req: DebugRequest) -> Optional[DebugResponse]:
        """Use Gemini or OpenAI to diagnose and repair broken code."""
        import json

        prompt = f"""You are an expert programming tutor and precise code debugger.
Analyze the following code (which may be in ANY language, e.g. Python, C, C++, Java, JavaScript, Rust, Go, etc.) and optional error trace.

STRICT DEBUGGING PRINCIPLES (AVOID FALSE POSITIVES):
1. ONLY FLAG REAL, FATAL ERRORS:
   - True Syntax / Compilation Errors: missing semicolons, unmatched parentheses/braces/brackets, invalid keywords, syntax errors that prevent compilation.
   - Definite Runtime Crashes: ZeroDivisionError, null/dangling pointer dereference, array index out of bounds, unhandled runtime exceptions.
   - Breaking Logic Bugs: loop bounds that go out of range, incorrect formulas that produce wrong output, infinite loops with no exit condition.
2. ABSOLUTELY DO NOT INVENT COMPILER WARNINGS OR NITPICK:
   - DO NOT flag standard language features (e.g. Variable Length Arrays `int arr[n]` in standard C99/C11, standard `scanf`/`printf`, normal pointer arithmetic).
   - DO NOT complain about missing input validation (e.g. "does not check if n <= 0") or lack of bounds checking on user input unless it causes a direct syntax or fatal runtime crash in the provided code.
   - DO NOT invent hypothetical compiler incompatibilities (e.g. MSVC vs GCC) or style preferences.
3. IF NO GENUINE ERROR EXISTS:
   - Set "has_bug": false
   - Set "error_type": "No Critical Errors Found"
   - Set "root_cause": "The code is valid and executes without critical runtime or compilation errors."
   - Set "fixed_code": exactly the user's original code without any modifications.
   - Set "explanation": "Your code is working properly and follows correct syntax and logic."
4. PRESERVE THE USER'S EXACT CODE STRUCTURE:
   - If there is a real bug, "fixed_code" MUST be an exact replica of the user's original code with ONLY the broken line(s) or character(s) fixed.
   - NEVER rewrite the entire architecture, NEVER replace simple arrays with `malloc`/heap allocation, and NEVER rename variables or reformat unchanged lines. Keep the student's code structure intact.

CODE:
```
{req.code}
```

OPTIONAL ERROR TRACE:
{req.error_message or "None provided"}

Return ONLY a valid JSON object matching this schema:
{{
  "language": "Detected language (e.g. C, C++, Python, JavaScript, Java)",
  "has_bug": true or false,
  "error_type": "Concise bug title (or 'No Critical Errors Found')",
  "root_cause": "Direct, 1-2 sentence explanation of the bug. No unnecessary filler.",
  "fixed_code": "The code with only the bug corrected (or exact original if no bug)",
  "explanation": "Brief explanation of what specific line was changed and why.",
  "prevention_tips": [
    "Practical habit 1",
    "Practical habit 2"
  ]
}}
"""
        for client, model, provider in self._get_llm_clients():
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                raw = completion.choices[0].message.content or "{}"
                
                # Clean markdown fences or extract JSON
                clean_raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
                clean_raw = re.sub(r"\s*```$", "", clean_raw)
                try:
                    data = json.loads(clean_raw)
                except Exception:
                    match = re.search(r"(\{[\s\S]*\})", raw)
                    data = json.loads(match.group(1)) if match else {}

                if not data:
                    continue

                has_bug = bool(data.get("has_bug", False))
                detected_lang = data.get("language") or req.language or "Code"

                return DebugResponse(
                    language=detected_lang,
                    difficulty=req.difficulty,
                    has_bug=has_bug,
                    error_type=data.get("error_type", "Syntax / Semantic Bug" if has_bug else "No Critical Errors Found"),
                    root_cause=data.get("root_cause", "Bug detected in code logic." if has_bug else "The code is syntactically valid and executes without critical runtime errors."),
                    fixed_code=data.get("fixed_code", req.code),
                    explanation=data.get("explanation", "Corrected syntax and logic flow." if has_bug else "No fixes needed."),
                    prevention_tips=data.get("prevention_tips", ["Test with minimal inputs."])
                )
            except Exception as e:
                print(f"[CodeTutor AI] LLM ({provider}) debug note: {e}. Trying next provider...")

        return None

    def _builtin_debug(self, req: DebugRequest) -> DebugResponse:
        """Rich local diagnostic engine with native AST parser and comprehensive bug detection."""
        code = req.code
        err = req.error_message or ""
        lang = req.language.lower()
        level = req.difficulty

        lines = code.split("\n")
        fixed_lines = list(lines)
        bug_found = False
        error_type = "Syntax / Logic Issue"
        root_cause = ""
        tips = [
            "Always run code with a minimal sample input first.",
            "Use a debugger or print statements to inspect variables at critical decision points.",
            "Check loop bounds and terminating conditions carefully."
        ]

        # 1. Native Python AST Compiler Check (only if definitely python or not containing C/Java syntax)
        is_non_python = any(marker in code for marker in ["#include", "int main(", "public static void", "System.out", "std::", "console.log", "function ", "const ", "let ", "printf(", "scanf("])
        if (lang == "python" or lang == "auto") and not is_non_python:
            import ast
            try:
                ast.parse(code)
            except SyntaxError as syn_err:
                bug_found = True
                line_no = syn_err.lineno or 1
                col_no = syn_err.offset or 1
                msg = syn_err.msg or "invalid syntax"
                error_type = f"SyntaxError: {msg.capitalize()}"
                bad_line = lines[line_no - 1] if line_no <= len(lines) else ""
                root_cause = (
                    f"Python encountered a syntax error at line {line_no} (column {col_no}): `{msg}`. "
                    f"Problematic line: `{bad_line.strip()}`."
                )

                # Intelligent single-line repair
                if any(bad_line.strip().startswith(k) for k in ["def ", "if ", "for ", "while ", "elif ", "else", "class ", "try", "except"]) and not bad_line.strip().endswith(":"):
                    fixed_lines[line_no - 1] = bad_line + ":"
                    error_type = "SyntaxError: Missing Colon (:)"
                    root_cause += " Python compound statements require a trailing colon `:` before an indented block."
                elif "=" in bad_line and "==" not in bad_line and any(k in bad_line for k in ["if ", "while ", "elif "]):
                    fixed_lines[line_no - 1] = re.sub(r"=\s*([^=])", r"== \1", bad_line, count=1)
                    error_type = "SyntaxError: Assignment instead of Equality (==)"
                    root_cause += " Single equals `=` is assignment; double equals `==` is required for equality comparison."
                elif bad_line.count("(") > bad_line.count(")"):
                    fixed_lines[line_no - 1] = bad_line + ")" * (bad_line.count("(") - bad_line.count(")"))
                    error_type = "SyntaxError: Unclosed Parenthesis"
                    root_cause += " Missing closing parenthesis `)`."
                elif bad_line.count("[") > bad_line.count("]"):
                    fixed_lines[line_no - 1] = bad_line + "]" * (bad_line.count("[") - bad_line.count("]"))
                    error_type = "SyntaxError: Unclosed Bracket"
                    root_cause += " Missing closing bracket `]`."

                tips = [
                    "Check the colon `:` at the end of block statements.",
                    "Ensure parentheses, brackets, and quotes are properly paired and closed.",
                    "Review indentation to ensure code blocks line up cleanly."
                ]

        # 2. Assignment in condition: if x = 100
        if not bug_found:
            for i, line in enumerate(lines):
                if re.search(r"^\s*(if|while|elif)\s+[a-zA-Z0-9_.]+\s*=\s*[^=]", line):
                    bug_found = True
                    error_type = "SyntaxError: Assignment instead of Equality Comparison (==)"
                    root_cause = (
                        "Single equals `=` is used for assigning values to variables. "
                        "In conditionals, you must use double equals `==` (or `===` in JavaScript) to compare values!"
                    )
                    fixed_lines[i] = re.sub(r"=\s*([^=])", r"== \1", line, count=1)
                    tips = [
                        "Remember: `=` assigns, `==` compares.",
                        "In JavaScript, prefer `===` for strict type-safe equality.",
                        "Linters and IDE highlighters flag assignment in conditional expressions."
                    ]
                    break

        # 3. Missing colon in Python
        if not bug_found and lang == "python":
            for i, line in enumerate(lines):
                stripped = line.strip()
                if any(stripped.startswith(k) for k in ["def ", "if ", "for ", "while ", "elif ", "else", "class ", "try", "except"]):
                    if not stripped.endswith(":") and not stripped.endswith(":\\") and not stripped.endswith("#"):
                        bug_found = True
                        error_type = "SyntaxError: Missing Colon (:)"
                        header_word = stripped.split()[0]
                        root_cause = (
                            f"Python compound statements starting with `{header_word}` must terminate with a colon `:`. "
                            "The colon informs Python that an indented block of code follows."
                        )
                        fixed_lines[i] = line + ":"
                        tips = [
                            "Every def, if, for, while, class, and try statement in Python requires a trailing colon.",
                            "Configure auto-formatting in your editor (e.g. Black or Ruff).",
                            "Look at the red squiggly line in your code editor—it often points to the missing colon."
                        ]
                        break

        # 4. Off-by-one loop: range(len(numbers) + 1) or <= len(numbers)
        if not bug_found:
            for i, line in enumerate(lines):
                if "range(len(" in line and "+ 1)" in line:
                    bug_found = True
                    error_type = "IndexError: Off-by-One Array Boundary in range()"
                    root_cause = (
                        "Lists/arrays are 0-indexed, with valid indices from `0` to `len - 1`. "
                        "Using `range(len(numbers) + 1)` attempts to access an index that does not exist on the last loop iteration."
                    )
                    fixed_lines[i] = line.replace("+ 1)", ")")
                    tips = [
                        "In Python, `range(len(arr))` already visits every valid index from 0 to len-1.",
                        "Prefer iterating directly: `for item in arr:` instead of index-based loops.",
                        "If you need both index and value, use `for idx, item in enumerate(arr):`."
                    ]
                    break
                elif "<= len(" in line or "<= arr.length" in line or "<= list.length" in line:
                    bug_found = True
                    error_type = "IndexError: Off-by-One Array Boundary (<= Length)"
                    root_cause = (
                        "Because array indices start at 0, the last element is at `length - 1`. "
                        "Using `<= length` tries to read an out-of-bounds element at the very end."
                    )
                    fixed_lines[i] = line.replace("<= len(", "< len(").replace("<= arr.length", "< arr.length").replace("<= list.length", "< list.length")
                    tips = [
                        "Use strict inequality `< length` when iterating with index counters.",
                        "Check your loop boundary condition before running.",
                        "Use modern iterator methods (`.forEach`, `for...of`) to eliminate index math."
                    ]
                    break

        # 5. Infinite while loop: counter checked but never updated
        if not bug_found:
            for i, line in enumerate(lines):
                if re.search(r"^\s*while\s+([a-zA-Z0-9_]+)\s*(<|<=|>|>=)\s*", line):
                    var_match = re.findall(r"while\s+([a-zA-Z0-9_]+)", line)
                    if var_match:
                        counter_var = var_match[0]
                        body = "\n".join(lines[i+1:])
                        if f"{counter_var} +=" not in body and f"{counter_var}++" not in body and f"{counter_var} -=" not in body and f"{counter_var} =" not in body:
                            bug_found = True
                            error_type = "Logical Error: Infinite While Loop"
                            root_cause = (
                                f"The while loop checks variable `{counter_var}`, but `{counter_var}` is never updated inside the loop body! "
                                "Because the condition remains True forever, the program freezes in an infinite loop."
                            )
                            indent = "    "
                            fixed_lines.append(f"{indent}{counter_var} += 1")
                            tips = [
                                "Always ensure loop counter variables are modified on every iteration.",
                                "Prefer `for` loops when the number of iterations is known in advance.",
                                "Add safety break conditions or timeout limits when writing while loops."
                            ]
                            break

        # 6. Unmatched delimiters (parentheses, brackets, braces)
        if not bug_found:
            open_parens = code.count("(")
            close_parens = code.count(")")
            open_brackets = code.count("[")
            close_brackets = code.count("]")
            open_braces = code.count("{")
            close_braces = code.count("}")

            if open_parens != close_parens:
                bug_found = True
                error_type = "SyntaxError: Mismatched Parentheses ()"
                root_cause = f"The code has {open_parens} opening parentheses `(` but {close_parens} closing parentheses `)`. Every opening parenthesis must have a matching closing pair."
            elif open_brackets != close_brackets:
                bug_found = True
                error_type = "SyntaxError: Mismatched Brackets []"
                root_cause = f"The code has {open_brackets} opening square brackets `[` but {close_brackets} closing brackets `]`. Lists and index accesses require balanced brackets."
            elif open_braces != close_braces:
                bug_found = True
                error_type = "SyntaxError: Mismatched Braces {}"
                root_cause = f"The code has {open_braces} opening curly braces `{{` but {close_braces} closing braces `}}`. Dictionaries and blocks require balanced braces."

        # 7. Parse user's terminal error trace if provided
        if not bug_found and err.strip():
            bug_found = True
            if "IndexError" in err:
                error_type = "IndexError: List Index Out of Range"
                root_cause = (
                    "An operation attempted to access an element at an index that doesn't exist in the list. "
                    "Remember that an N-element list only has indices from 0 to N-1."
                )
            elif "KeyError" in err:
                error_type = "KeyError: Key Not Found in Dictionary"
                root_cause = (
                    "You attempted to look up a key with `dict[key]` that doesn't exist. "
                    "Use `dict.get(key, default)` for safe lookups without throwing errors."
                )
            elif "TypeError" in err:
                error_type = "TypeError: Incompatible Data Types"
                root_cause = (
                    "An operation was performed on mismatched types (e.g. concatenating a string with a number). "
                    "Ensure variables are cast to the expected type using `str()`, `int()`, etc."
                )
            elif "ZeroDivisionError" in err:
                error_type = "ZeroDivisionError: Division by Zero"
                root_cause = "A division or modulo operation was executed with a denominator of 0, which is undefined in mathematics."
            elif "NameError" in err:
                error_type = "NameError: Undefined Variable"
                root_cause = "You referenced a variable or function name that has not been defined in the current scope. Check for spelling errors or missing imports."
            else:
                error_type = "Runtime Failure"
                root_cause = f"Terminal trace indicated an execution failure: {err.strip()[:120]}"

        if not bug_found and not err.strip():
            return DebugResponse(
                language=lang,
                difficulty=level,
                has_bug=False,
                error_type="No Critical Syntax Bug Detected",
                root_cause="The code appears syntactically valid and structured cleanly! If it produces incorrect calculations, check algorithmic edge cases or provide the terminal error message.",
                fixed_code=code,
                explanation="We inspected for assignment errors, missing colons, unbounded while loops, unclosed brackets, and out-of-range indices.",
                prevention_tips=[
                    "Write unit tests with edge-case inputs (e.g. empty lists, zero, negative numbers).",
                    "Step through the execution using a debugger or log statements.",
                    "Paste specific terminal error traces if you encounter a runtime failure."
                ]
            )

        fixed_code = "\n".join(fixed_lines)
        explanation = (
            f"**Root Cause**: {root_cause}\n\n"
            f"**How it was fixed**: We updated the code so the syntax complies with {lang.capitalize()} specifications "
            f"and the algorithm executes safely without throwing exceptions."
        )

        return DebugResponse(
            language=lang,
            difficulty=level,
            has_bug=True,
            error_type=error_type,
            root_cause=root_cause,
            fixed_code=fixed_code,
            explanation=explanation,
            prevention_tips=tips
        )

tutor_engine = TutorEngine()

