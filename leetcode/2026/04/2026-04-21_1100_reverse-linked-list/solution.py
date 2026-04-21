class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def reverseList(head):
    if not head or not head.next:
        return head
    prev = None
    curr = head
    while curr:
        temp = curr.next
        curr.next = prev
        prev = curr
        curr = temp
    return prev