class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None
def reverseList(head):
    prev = None
    curr = head
    while curr is not None:
        temp = curr.next
        curr.next = prev
        prev = curr
        curr = temp
    return prev