class Payment:
    def __init__(self,price):
        self.__final_price = price*1.05
    def fp(self):
        return (self.__final_price)
    def sale(self):
        self.__final_price=self.__final_price*0.9
book=Payment(10)
#print(book.__final_price)
print(book.fp())
book.sale()
print(book.fp())