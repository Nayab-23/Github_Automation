# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        prev=None
        current=head
        while current is not None:
            temp=current.next
            current.next=prev
            prev=current
            current=temp
        return prev