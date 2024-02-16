from search_and_print import SearchAndPrint

class Program:

    name = input("Qual o nome do medicamento? -> ")
    brand = input("Qual a marca do medicamento? -> ")

    instance = SearchAndPrint()
    instance.search_and_print_register(name, brand)
