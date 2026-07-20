from typing import Optional
from collections import deque
def reverseList(head: Optional[ListNode]) -> ListNode:
    nodes = deque()
    while head is not None:
        nodes.append(head)
        head = head.next
    prev = None
    while nodes:
        node = nodes.pop()
        node.next = prev
        prev = node
    return prev