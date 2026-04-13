from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    current = head

    while current is not None:
        temp = current.next
        current.next = prev
        prev = current
        current = temp

    return prev