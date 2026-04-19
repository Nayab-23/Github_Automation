def two_sum(nums, target):
    # Create a dictionary to store the complement of each number
    num_complement_dict = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_complement_dict:
            return [num_complement_dict[complement], i]
        num_complement_dict[num] = i
    
    # If no two numbers sum up to the target, return None or raise an exception as per requirement.
    # In this case, we will return None since the problem statement does not specify the behavior in such cases.
    return None