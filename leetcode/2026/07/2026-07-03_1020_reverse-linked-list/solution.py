class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        curr = head
        prev = None
        while curr is not None:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        return prev