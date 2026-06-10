class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None
def reverseList(head):
    if not head or not head.next:
        return head
    prev, curr = None, head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev