def base(n: int) ->str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if n == 0:
        return "0"
    else :

        result = ""

        while n>0:
            remainder = n%62
            result = alphabet[remainder] + result
            n = n//62

        return result