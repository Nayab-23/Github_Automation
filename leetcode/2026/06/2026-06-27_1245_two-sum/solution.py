def two_sum(nums, target):
    # Create a dictionary to store numbers and their indices
    num_indices = {}
    
    # Iterate through the list of numbers
    for i, num in enumerate(nums):
        complement = target - num
        
        # Check if the complement is already in the dictionary
        if complement in num_indices:
            return [num_indices[complement], i]
        
        # If not, add the current number and its index to the dictionary
        num_indices[num] = i
    
    # If no pair is found, return an empty list
    return []