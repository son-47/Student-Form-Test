

field_alias = {'co': 'code', 'na': 'name', 'de': 'description', 'wr': 'write_date'}
columnlist = "co , na,  de"
# columns = []
# for alias in columnlist.split(','):
#     field = field_alias.get(alias.strip())
#     columns.append(field)
# print(columns)
try:
    try:
        x = int(input("Enter a number: "))
        print("You entered:", x)
    except Exception :
        raise ValueError("lỗi không phải int")
except ValueError as ve:
    print(ve)
except Exception as e:
    print(e)
        

# try:
#     x = int(input("Enter a number: "))
#     print("You entered:", x)
# except Exception as e:
#     raise TypeError("lỗi không phải int")
#     print(e)
