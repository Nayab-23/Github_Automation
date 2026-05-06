def reverseList(head):

    # Initialize pointers to keep track of the previous, current, and next nodes
    prev = None
    curr = head
    next_node = None

    # Traverse the list while we have more than one node
    while curr is not None:
        # Store the next node before we overwrite curr.next
        next_node = curr.next

        # Reverse the current node's pointer to point to the previous node
        curr.next = prev

        # Move the pointers one step forward
        prev = curr
        curr = next_node

    return prev