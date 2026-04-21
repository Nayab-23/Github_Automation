class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def reverseList(head):
    prev, curr = None, head
    while curr:
        next = curr.next
        curr.next = prev
        prev = curr
        curr = next
    return prev