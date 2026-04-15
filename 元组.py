"""
从左到右，按位置一个一个比谁先分出大小，整个元组的大小就定了，后面不再比。
"""

"""
# 定义一个三元组
t1 = (35, 12, 98)
# 定义一个四元组
t2 = ('映枝',19, True, 'China')

# 查看变量的类型
print(type(t1))  # <class 'tuple'>
print(type(t2))  # <class 'tuple'>

# 查看元组中元素的数量
print(len(t1))  # 3
print(len(t2))  # 4

# 索引运算
print(t1[0])    # 35
print(t1[2])    # 98
print(t2[-1])   # China

# 切片运算
print(t2[:2])   # ('映枝', 19)
print(t2[::3])  # ('映枝', 'China')

# 循环遍历元组中的元素
for elem in t1:
    print(elem)

# 成员运算
print(12 in t1)         # True
print(99 in t1)         # False
print('Hao' not in t2)  # True

# 拼接运算
t3 = t1 + t2
print(t3)  # (35, 12, 98,'映枝',19, True, 'China' )

# 比较运算
print(t1 == t3)            # False
print(t1 >= t3)            # False
print(t1 <= (35, 11, 99))  # False
"""

"""
()为空元组，有几个元素被称为几元组，如果只有一个元素则需要在该元素后面加上“,”才表示一元组，
否则()就不是代表元组的字面量语法，而是改变运算优先级的圆括号
"""

"""
a = ()
print(type(a))  # <class 'tuple'>
b = ('hello')
print(type(b))  # <class 'str'>
c = (100)
print(type(c))  # <class 'int'>
d = ('hello', )
print(type(d))  # <class 'tuple'>
e = (100, )
print(type(e))  # <class 'tuple'>
"""

"""
# 打包操作
a = 1, 10, 100
print(type(a))  # <class 'tuple'>
print(a)        # (1, 10, 100)
# 解包操作
i, j, k = a
print(i, j, k)  # 1 10 100
"""

"""
首先，用星号表达式修饰的变量会变成一个列表，列表中有0个或多个元素；其次，在解包语法中，星号表达式只能出现一次。
这可以用来解决变量个数少于元素个数的问题
"""
"""
a = 1, 10, 100, 1000
i, j, *k = a
print(i, j, k)        # 1 10 [100, 1000]
i, *j, k = a
print(i, j, k)        # 1 [10, 100] 1000
*i, j, k = a
print(i, j, k)        # [1, 10] 100 1000
*i, j = a
print(i, j)           # [1, 10, 100] 1000
i, *j = a
print(i, j)           # 1 [10, 100, 1000]
i, j, k, *l = a
print(i, j, k, l)     # 1 10 100 [1000]
i, j, k, l, *m = a
print(i, j, k, l, m)  # 1 10 100 1000 []
"""

"""
a, b, *c = range(1, 10)
print(a, b, c)
a, b, c = [1, 10, 100]
print(a, b, c)
a, *b, c = 'hello'
print(a, b, c)
"""

"""
通过打包和解包的方式来进行变量值的交换，“=”左侧打包成元组，右侧解包实现值交换
"""
"""
a = 10
b = 20
c = 30
# 打包 + 解包，直接交换
a, b = b, a
print(a)  # 20
print(b)  # 10
a, b, c = b, c, a
print(a)  # 10
print(b)  # 30
print(c)  # 20
"""

"""
infos = ('映枝', 19, True, 'China')
# 将元组转换成列表
print(list(infos))  # ['骆昊', 45, True, '四川成都']

frts = ['apple', 'banana', 'orange']
# 将列表转换成元组
print(tuple(frts))  # ('apple', 'banana', 'orange')
"""


"""
列表是可变数据类型，元组是不可变数据类型
"""