#1 2 3 4 5\n
#[1][ 2][ 3][ 4][ 5][\n]
#法一
first = True
for i in range(a, c+1, b):
  if first:
    first = False
    print(i, end = "")
  else:
    print(' ' + i, end = "")
print()


#[1 ][2 ][3 ][4 ][5 \n]
# 法二
for i in range(a, c+1, b):
  if i + b > c:
    print(i) # i\n
  else:
    print(i, end = " ")


#[1 ][2 ][3 ][4 ][5 \n]
#法三
for i in range(a, c, b):
  print(i, end=" ")
print(c)


#[1 ][2 ][3 ][4 ][5 \n]
#法四
s = ""
for i in range(a, c+1, b):
  if i + b > c:
    s += str(i)+'\n'
  else:
    s += str(i) + ' '
print(s)

