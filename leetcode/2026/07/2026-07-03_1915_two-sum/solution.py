def twoSum(nums, target):
    num_dict = {}
    for i in range(len(nums)):
        if target - nums[i] in num_dict:
            return [num_dict[target - nums[i]], i]
        num_dict[nums[i]] = i