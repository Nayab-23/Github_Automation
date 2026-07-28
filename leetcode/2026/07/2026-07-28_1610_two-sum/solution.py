def two_sum(nums, target):

    # Create a dictionary to store the complement of each number and its index
    complement_map = {}

    for i in range(len(nums)):
        complement = target - nums[i]

        # Check if the complement exists in the map
        if complement in complement_map:
            return [complement_map[complement], i]

        # Store the current number and its index in the dictionary
        complement_map[nums[i]] = i

    # If no solution is found, return an empty list
    return []