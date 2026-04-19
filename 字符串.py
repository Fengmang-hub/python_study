"""
s1 = '\'hello, world!\''
s2 = '\\hello, world!\\'
print(s1)
print(s2)
"""

"""
s1 = 'hello, world!'
s2 = "你好，世界！❤️"
s3 = '''hello,
wonderful
world!'''
print(s1)
print(s2)
print(s3)
"""

'''
s1 = '\it \is \time \to \read \now'
s2 = r'\it \is \time \to \read \now'
print(s1)
print(s2)
'''

'''
s1 = 'hello' + ', ' + 'world'
print(s1)    # hello, world
s2 = '!' * 3
print(s2)    # !!!
s1 += s2
print(s1)    # hello, world!!!
s1 *= 2
print(s1)    # hello, world!!!hello, world!!!
'''

'''
s1 = 'a whole new world'
s2 = 'hello world'
print(s1 == s2)             # False
print(s1 < s2)              # True
print(s1 == 'hello world')  # False
print(s2 == 'hello world')  # True
print(s2 != 'Hello world')  # True
s3 = '映枝'
print(ord('映'))            # 26144
print(ord('枝'))            # 26525
s4 = '王大锤'
print(ord('王'))            # 29579
print(ord('大'))            # 22823
print(ord('锤'))            # 38180
print(s3 >= s4)             # False
print(s3 != s4)             # True
'''

'''
s1 = 'hello, world'
s2 = 'goodbye, world'
print('wo' in s1)      # True
print('wo' not in s2)  # False
print(s2 in s1)        # False
print(' w' in s1)      # True
print('  w' in s1)     # False
'''

'''
s = 'hello, world'
print(len(s))                 # 12
print(len('goodbye, world'))  # 14
'''

'''
字符串是不可变类型，所以不能通过索引运算修改字符串中的字符
'''

'''
s = 'abc123456'
n = len(s)
print(s[0], s[-n])    # a a
print(s[n-1], s[-1])  # 6 6
print(s[2], s[-7])    # c c
print(s[5], s[-4])    # 3 3
print(s[2:5])         # c12
print(s[-7:-4])       # c12
print(s[2:])          # c123456
print(s[:2])          # ab
print(s[::2])         # ac246
print(s[::-1])        # 654321cba
'''

'''
遍历字符串中的每个字符1.0
'''

'''
s = 'hello'
for i in range(len(s)):
    print(s[i])
'''

'''
遍历字符串中的每个字符2.0
'''

'''
s = 'hello'
for elem in s:
    print(elem)
'''

'''
字符串是不可变类型，使用字符串的方法对字符串进行操作会产生新的字符串，但是原来变量的值并没有发生变化。
'''

'''
s1 = 'hello, world!'
# 字符串首字母大写
print(s1.capitalize())  # Hello, world!
# 字符串每个单词首字母大写
print(s1.title())       # Hello, World!
# 字符串变大写
print(s1.upper())       # HELLO, WORLD!
s2 = 'GOODBYE'
# 字符串变小写
print(s2.lower())       # goodbye
# 检查s1和s2的值
print(s1)               # hello, world
print(s2)               # GOODBYE
'''

'''
find方法找不到指定的字符串会返回-1，index方法找不到指定的字符串会引发ValueError错误。
'''
'''
s = 'hello, world!'
print(s.find('or'))      # 8
print(s.find('or', 9))   # -1
print(s.find('or',8))
print(s.find('of'))      # -1
print(s.index('or'))     # 8
print(s.index('or', 9))  # ValueError: substring not found
'''

'''
s = 'hello world!'
print(s.find('o'))       # 4
print(s.rfind('o'))      # 7
print(s.rindex('o'))     # 7
# print(s.rindex('o', 8))  # ValueError: substring not found
'''

'''
上面的isdigit用来判断字符串是不是完全由数字构成的
isalpha用来判断字符串是不是完全由字母构成的，这里的字母指的是 Unicode 字符但不包含 Emoji 字符
isalnum用来判断字符串是不是由字母和数字构成的。
'''
'''
s1 = 'hello, world!'
print(s1.startswith('He'))   # False
print(s1.startswith('hel'))  # True
print(s1.endswith('!'))      # True
s2 = 'abc123456'
print(s2.isdigit())  # False
print(s2.isalpha())  # False
print(s2.isalnum())  # True
'''

'''
zfill 会识别正负号，把 0 补在符号和数字中间，而不是符号前面
'''
'''
s = 'hello, world'
print(s.center(20, '*'))  # ****hello, world****
print(s.rjust(20))        #         hello, world
print(s.ljust(20, '~'))   # hello, world~~~~~~~~
print('33'.zfill(5))      # 00033
print('-33'.zfill(5))     # -0033
'''

'''
字符串的strip方法可以帮我们获得将原字符串修剪掉左右两端指定字符之后的字符串，默认是修剪空格字符。
'''

'''
s1 = '   china666  '
print(s1)
print(s1.strip())      # china666
s2 = '~你好，世界~'
print(s2.lstrip('~'))  # 你好，世界~
print(s2.rstrip('~'))  # ~你好，世界
'''

'''
s = 'hello, good world'
print(s.replace('o', '@'))     # hell@, g@@d w@rld
print(s.replace('o', '@', 1))  # hell@, good world
'''

'''
split方法默认使用空格进行拆分，我们也可以指定其他的字符来拆分字符串，而且还可以指定最大拆分次数来控制拆分的效果，代码如下所示。
'''

'''
s = 'I love you'
words = s.split()
print(words)            # ['I', 'love', 'you']
print('~'.join(words))  # I~love~you
s = 'I#love#you#so#much'
words = s.split('#')
print(words)  # ['I', 'love', 'you', 'so', 'much']
words = s.split('#', 2)
print(words)  # ['I', 'love', 'you#so#much']
'''

'''
a = '映枝'
b = a.encode('utf-8')
c = a.encode('gbk')
print(b)                  # b'\xe6\x98\xa0\xe6\x9e\x9d'
print(c)                  # b'\xd3\xb3\xd6\xa6'
print(b.decode('utf-8'))  # 映枝
print(c.decode('gbk'))    # 映枝
'''