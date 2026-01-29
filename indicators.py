def avg(N,listInsert):
    """
    Calculate an average given a current day (N)

    listInsert should contain all historical prices up to day N

    
    :param N: current day numbers
    :param listInsert: list of all historical prices
    """
    result=0
    for i in range(len(listInsert)):
        if(i==0):
            continue
        else:
            result+=(listInsert[N-i-1][1])
    result=result/(N-1)
    return result
