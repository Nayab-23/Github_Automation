from typing import List

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def reverseList(head: ListNode) -> ListNode:
    prev, curr = None, head
    while curr is not None:
        temp = curr.next
        curr.next = prev
        prev = curr
        curr = temp
    return prev