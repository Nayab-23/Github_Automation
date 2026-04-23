def twoSum(nums, target):
    num_dict = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[n] = i
    raise ValueError('No solution')

print(twoSum([2,7,11,15], 9))