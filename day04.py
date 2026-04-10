import math

"""
first:
print(321 + 12)     # 加法运算，输出333
print(321 - 12)     # 减法运算，输出309
print(321 * 12)     # 乘法运算，输出3852
print(321 / 12)     # 除法运算，输出26.75
print(321 // 12)    # 整除运算，输出26
print(321 % 12)     # 求模运算，输出9
print(321 ** 12)    # 求幂运算，输出1196906950228928915420617322241
"""

"""
算术运算的优先级
print(2 + 3 * 5)           # 17
print((2 + 3) * 5)         # 25
print((2 + 3) * 5 ** 2)    # 125
print(((2 + 3) * 5) ** 2)  # 625
"""

"""
赋值运算符和复合赋值运算符
a = 10
b = 3
a += b        # 相当于：a = a + b
a *= a + 2    # 相当于：a = a * (a + 2)
print(a)      # 大家算一下这里会输出什么
"""

"""
海象运算符
# SyntaxError: invalid syntax
# print((a = 10))
# 海象运算符
print((a := 10))  # 10
print(a)          # 10
"""

"""
比较运算符和逻辑运算符的使用

逻辑运算符有三个，分别是and、or和not。and字面意思是“而且”，所以and运算符会连接两个布尔值或者产生布尔值的表达式，
如果两边的布尔值都是True，那么运算的结果就是True；左右两边的布尔值有一个是False，最终的运算结果就是False。
当然，如果and运算符左边的布尔值是False，不管右边的布尔值是什么，最终的结果都是False，
这时运算符右边的布尔值会被跳过（专业的说法叫短路处理，如果and右边是一个表达式，那么这个表达式不会执行）。
or字面意思是“或者”，所以or运算符也会连接两个布尔值或产生布尔值的表达式，如果两边的布尔值有任意一个是True，那么最终的结果就是True。
当然，or运算符也是有短路功能的，当它左边的布尔值为True的情况下，右边的布尔值会被短路（如果or右边是一个表达式，那么这个表达式不会执行）。
not运算符的后面可以跟一个布尔值，如果not后面的布尔值或表达式是True，那么运算的结果就是False；
如果not后面的布尔值或表达式是False，那么运算的结果就是True。
flag0 = 1 == 1
flag1 = 3 > 2
flag2 = 2 < 1
flag3 = flag1 and flag2
flag4 = flag1 or flag2
flag5 = not flag0
print('flag0 =', flag0)     # flag0 = True
print('flag1 =', flag1)     # flag1 = True
print('flag2 =', flag2)     # flag2 = False
print('flag3 =', flag3)     # flag3 = False
print('flag4 =', flag4)     # flag4 = True
print('flag5 =', flag5)     # flag5 = False
print(flag1 and not flag2)  # True
print(1 > 2 or 2 == 3)      # False
"""

"""
将华氏温度转换为摄氏温度
f = float(input('请输入华氏温度: '))
c = (f - 32) / 1.8
print('%.1f华氏度 = %.1f摄氏度' % (f, c))  %(f,c)会将（）里的内容按照顺序替换到%.1f处
"""

"""
将华氏温度转换为摄氏温度
f = float(input('请输入华氏温度: '))
c = (f - 32) / 1.8
print(f'{f:.1f}华氏度 = {c:.1f}摄氏度')
"""

"""
输入半径计算圆的周长和面积
radius = float(input('请输入圆的半径: '))
perimeter = 2 * 3.1416 * radius
area = 3.1416 * radius * radius
print('周长: %.2f' % perimeter)
print('面积: %.2f' % area)
"""

"""
radius = float(input('请输入圆的半径: '))
perimeter = 2 * math.pi * radius
area = math.pi * radius ** 2
print(f' {perimeter = :.2f}') 加了=就会同时输出变量名和变量值。不加=就只有变量值
print(f' {area = :.2f}')
"""

"""
输入年份，闰年输出True，平年输出False
year = int(input('请输入年份: '))
is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
print(f'{is_leap = }')
"""