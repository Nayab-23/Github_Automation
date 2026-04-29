class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None
def reverseList(head):
    prev = None
    current = head
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    return prev