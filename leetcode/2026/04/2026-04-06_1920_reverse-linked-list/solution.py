def reverseList(head):
    if not head or not head.next:
        return head
    prev, curr = None, head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev