
def add_branch_prefix(history, i):
    new_hist = set(map(lambda order, info : (f'{i}#' + order, info), history))
    return new_hist