class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None
class Solution(object):
    def reverseList(self, head):
        prev = None
        curr = head
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        return prev