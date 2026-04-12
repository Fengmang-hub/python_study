"""
append是在列表末尾追加元素，insert则是在特定位置插入
"""
"""
languages = ['Python', 'Java', 'C++']
languages.append('JavaScript')
print(languages)  # ['Python', 'Java', 'C++', 'JavaScript']
languages.insert(1, 'SQL')
print(languages)  # ['Python', 'SQL', 'Java', 'C++', 'JavaScript']
"""

"""
remove可以删除指定元素；pop默认删除列表中的最后一个元素，也可以给一个位置删除指定位置的元素；clear则是清空列表
"""
"""
languages = ['Python', 'SQL', 'Java', 'C++', 'JavaScript']
if 'Java' in languages:
    languages.remove('Java')
if 'Swift' in languages:
    languages.remove('Swift')
print(languages)  # ['Python', 'SQL', C++', 'JavaScript']
languages.pop()
print(languages)
temp = languages.pop(1)
print(temp)       # SQL
languages.append(temp)
print(languages)  # ['Python', C++', 'SQL']
languages.insert(2,'agent')
print(languages)
languages.pop(1)
print(languages)
languages.clear()
print(languages)  # []
"""

"""
如果有两个相同的元素，remove会删除第一个，再进行remove则一次往后按顺序删除
"""
"""
items = ['Python', 'Java', 'C++','Python']
del items[1]
print(items)  # ['Python', 'C++']
items.remove('Python')
print(items)
items.remove('Python')
print(items)
"""

"""
错误，因为正向删除会导致索引消失，导致无法走完循环
items = ['Python', 'Java', 'C++','Python','C']
for _ in items:
    items.remove('Python')
print(items)
"""
"""
正确的删除应该用reversed倒序删除
"""
"""
items = ['Python', 'Java', 'C++','Python','C']
for i in reversed(range(len(items))):
    if items[i] == 'Python':
        del items[i]
print(items)
"""