def custom_fence(fence: str = "+"):
    def add_fence(func):
       def wrapper():
         print(fence * 10)
         func()
         print(fence * 10)
       return wrapper
    return add_fence



@custom_fence("=")
def log():
    print("decorated?")


log()

# def fence(func):
#     def wrapper():
#         print("hi there")
#         func()

#     return wrapper


# def log():
#     print("decorated?")


# log = fence(log)

# log()