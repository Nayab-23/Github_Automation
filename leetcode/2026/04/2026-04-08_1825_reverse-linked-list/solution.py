from typing import Optional

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    curr = head
    while curr is not None:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev