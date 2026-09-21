import markdown
from xhtml2pdf import pisa

def create_pdf(markdown_content, output_filename):
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
    # Wrap in basic HTML structure
    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1 {{ color: #2c3e50; font-size: 24px; border-bottom: 2px solid #2c3e50; padding-bottom: 5px;}}
        h2 {{ color: #34495e; font-size: 20px; margin-top: 20px; }}
        h3 {{ color: #7f8c8d; font-size: 16px; }}
        pre {{ background-color: #f8f9fa; padding: 10px; border: 1px solid #e9ecef; border-radius: 5px; }}
        code {{ font-family: monospace; background-color: #f8f9fa; padding: 2px 4px; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """
    
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html, dest=result_file)
        
    if pisa_status.err:
        print("Error during PDF generation")
    else:
        print(f"Successfully generated {output_filename}")

solutions_md = """
# DSA Question Papers Solutions

This document contains solutions to the Data Structure and Algorithm mid-semester examination papers.

## Autumn Mid-Semester Examination - 2024

**1. Answer all the questions:**
**a)** The worst-case time complexity is `O(n log log n)`. The outer loop runs `n` times. In the inner loop, `j` is repeatedly raised to the power of `k` (since `k=3`), meaning the number of steps to reach `n` is logarithmic logarithm: `O(log_k(log_j n))`.
**b)** The matrix is `B[12][12]` stored in Row Major Order, and 8 bytes per element. Base address can be found from `B[3][3] = 1140`. Offset from B[0][0] to B[3][3] is `(3*12 + 3) * 8 = 39 * 8 = 312`. So, Base = `1140 - 312 = 828`. The address of `B[5][5]` is `Base + (5*12 + 5)*8 = 828 + 65*8 = 1348`.
**c)** Pseudocode to convert Single Linked List to Circular:
```c
Node* temp = head;
if (head == NULL) return;
while (temp->next != NULL) {
    temp = temp->next;
}
temp->next = head;
```
**d)** C function to reverse a string using a Stack:
```c
void reverseString(char* str) {
    int n = strlen(str);
    Stack s; init(&s);
    for(int i=0; i<n; i++) push(&s, str[i]);
    for(int i=0; i<n; i++) str[i] = pop(&s);
}
```
**e)** Pushed: 11, 12, 13, 14, 15, 16. Popped 5 times: 16, 15, 14, 13, 12. Inserted in queue: 16, 15, 14, 13, 12. Queue deletes 3 elements: 16, 15, 14. These are pushed to stack (which has 11). Stack now has: 11, 16, 15, 14 (14 at top). Two items popped: 14 and 15. The popped items are **14 and 15**.

**4. (a) Infix to Postfix conversion for `a * b / (a - c) + d * b`:**
- Step 1: Scan `a`, Postfix: `a`
- Step 2: Scan `*`, Stack: `*`
- Step 3: Scan `b`, Postfix: `a b`
- Step 4: Scan `/`, Stack: `/` (since / has same precedence as *, pop * and push /), Postfix: `a b *`
- Step 5: Scan `(`, Stack: `/ (`
- Step 6: Scan `a`, Postfix: `a b * a`
- Step 7: Scan `-`, Stack: `/ ( -`
- Step 8: Scan `c`, Postfix: `a b * a c`
- Step 9: Scan `)`, Pop until `(`, Stack: `/`, Postfix: `a b * a c -`
- Step 10: Scan `+`, Pop `/` and push `+`, Stack: `+`, Postfix: `a b * a c - /`
- Step 11: Scan `d`, Postfix: `a b * a c - / d`
- Step 12: Scan `*`, Stack: `+ *`
- Step 13: Scan `b`, Postfix: `a b * a c - / d b`
- Step 14: End of string, pop all: `a b * a c - / d b * +`

**4. (b) Evaluate postfix `a b * a c - / d b * +` where a=2, b=3, c=1, d=5:**
Postfix: `2 3 * 2 1 - / 5 3 * +`
- Push 2, Push 3. Encounter `*`: 2 * 3 = 6. Push 6.
- Push 2, Push 1. Encounter `-`: 2 - 1 = 1. Push 1.
- Encounter `/`: 6 / 1 = 6. Push 6.
- Push 5, Push 3. Encounter `*`: 5 * 3 = 15. Push 15.
- Encounter `+`: 6 + 15 = 21. Push 21.
Result: **21**.

## Autumn Mid-Semester Examination - 2023

**1. a)** Correct option: **A) O(1)** - Accessing an arbitrary element in an array takes O(1) time.
**b)** Address of `arr[8][6]` in column major order for `arr[1...10][1...15]`: Base + Size * (Rows * (Col - lower_col) + (Row - lower_row)).
`100 + 2 * (10 * (6 - 1) + (8 - 1)) = 100 + 2 * (50 + 7) = 100 + 114 = 214`.
**c)** Output of disp function for 10->20->30->40->50: 
The function prints `head->info`, recursively calls `disp(head->next->next)`, and prints `head->info` again. 
Call trace: disp(10) -> prints 10, calls disp(30), prints 10. disp(30) -> prints 30, calls disp(50), prints 30. disp(50) -> prints 50, calls disp(NULL), prints 50. 
Overall Output: **10 30 50 50 30 10**.
**d)** The code inserts a new node to the **A) Right to mid**.
**e)** Initial Stack: 5, 7, 3 (3 at top). Max capacity = 6.
push(4) -> Stack: [5, 7, 3, 4]
pop() -> returns 4. Stack: [5, 7, 3]
push(10) -> Stack: [5, 7, 3, 10]
push(8) -> Stack: [5, 7, 3, 10, 8]
push(0) -> Stack: [5, 7, 3, 10, 8, 0]
push(9) -> Capacity exceeded, overflow occurs. Stack remains unchanged.
pop() -> returns 0.
pop() -> returns 8.
Outputs of pop operations: **4, 0, 8**.

**2. a)** The outer loop runs `n` times. The first inner loop increments `p` logarithmically `O(log_2 n)` times. The second inner loop increments `q` logarithmically based on `p`, `O(log_2 p)` times. Hence `q` accumulates `n * log_2(log_2 n)` times.
Return value is **O(n log log n)**.

## Autumn Mid-Semester Examination - 2022

**1. a)** Time complexity of the function: Infinite loop! The variable `i` is initialized to 1 and the condition is `while(i<=n)`. However, `i` is never incremented inside the loop. The complexity is `O(∞)`. If it was a typo and `i` was incremented, the inner loop runs `√n` times, giving `O(n√n)`.
**b)** Address of `arr[5][3]` for `arr[3...6][-2...5]` (Row Major). Total columns = 5 - (-2) + 1 = 8. Rows = 4. 
`Loc = 1001 + 4 * (8 * (5 - 3) + (3 - (-2))) = 1001 + 4 * (16 + 5) = 1085`.

## DSA Midsem Question 2020

**2. a)** Address of `B[5][4]` column major. `B[10][20]`, 4 bytes. `B[2][1] = 2140`. 
Base address: `2140 = Base + 4 * (10*1 + 2) => Base = 2092`.
`B[5][4] = 2092 + 4 * (10*4 + 5) = 2092 + 180 = 2272`.

## Autumn Mid-Semester 2019

**1. a)** Time complexity of `for(i=1; i<=m; i=i*2) { for(j=1; j<=i; j++) ... }`: The inner loop executes `i` times, where `i` takes values 1, 2, 4, 8... up to `m`. Sum of this geometric series is `2m - 1`. Time complexity is **O(m)**.
**1. b)** Relation between row-major and column-major cell indices. If `A[i][j]` is the same, then `C*i + j = R*j + i`. For a square matrix (R=C), this holds true for diagonal elements where `i = j`. Example: for 3x3 matrix, index `(1,1)` maps to position `3*1 + 1 = 4` in both orders.

---
*Note: This is a consolidated and summarized version of the solutions covering the main logic and theoretical questions across the provided papers.*
"""

create_pdf(solutions_md, "d:/flood/solutions.pdf")
