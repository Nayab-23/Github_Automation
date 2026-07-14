def reverse_linked_list(head):
    if head is None or head.next is None:
        return head
    prev = None
    curr = head
    while curr is not None:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    head = prev
    return head