
''''二分查找'''
def binarySearch(alist, item):
    first = 0
    last = len(alist) - 1
    while first <= last:
        mid_point = (first+last)//2
        if alist[mid_point] == item:
            return True
        elif item < alist[mid_point]:
            last = mid_point - 1
        else:
            first = mid_point + 1
    return False

'''冒泡排序'''
def bubbleSort(array:list):
    n = len(array)
    for i in range(n):
        for j in range(0, n-i-1):
            if array[j] > array[j+1] :
                array[j], array[j+1] = array[j+1], array[j]
    return array

'''快速排序'''
def quickSort(array:list):
    if len(array) < 2:
        return array
    else:
        pivot = array[0]
        less = [i for i in array[1:] if i < pivot]
        greater = [i for i in array[1:] if i>pivot]
        return quickSort(less)+[pivot]+quickSort(greater)

'''
二叉树 红黑树 等
'''

''''元组去重'''
def deleteDuplicate(l): return [dict(t) for t in set([tuple(d.items()) for d in l])]