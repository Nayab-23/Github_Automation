def two_sum(nums, target):
    # Dictionary to store the complement of each number and its index
    seen = {}
    
    for i, num in enumerate(nums):
        if (complement := target - num) in seen:
            return [seen[complement], i]
        seen[num] = i