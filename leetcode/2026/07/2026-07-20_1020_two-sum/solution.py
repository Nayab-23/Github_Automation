def twoSum(nums, target):
    # Dictionary to store the difference and its index
    num_dict = {}

    for i in range(len(nums)):
        complement = target - nums[i]

        if complement in num_dict:
            return [num_dict[complement], i]

        num_dict[nums[i]] = i

    # If no two numbers add up to the target, return an empty list
    return []