def reverseList(head):
	current = head
	prev = None
	while current is not None:
		next_node = current.next
		previous, current.next, current = current, previous, next_node
	return prev