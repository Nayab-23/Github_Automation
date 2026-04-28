def reverseList(head):
    # Initialize pointers for reversing
    prev = None
    current = head
    while current:
        # Store the next node before reversing
        temp = current.next
        # Reverse the link of the current node
        current.next = prev
        # Move prev and current to the next nodes
        prev = current
        current = temp
    return prev