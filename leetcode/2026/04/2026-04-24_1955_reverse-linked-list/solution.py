def reverse_linked_list(head):
    if not head or not head.next:
        return head
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev