def ramped_half_and_half(pset, type_=None, min_=1, max_=6):
    if type_ is None:
        type_ = pset.ret
    expr = None
    height = random.randint(min_, max_)
    method = random.choice([gp.genGrow, gp.genFull])
    expr = method(pset, min_=height, max_=height, type_=type_)
    return expr


"""Population
│
├─ upper_pop: [Individual_1, Individual_2, ..., Individual_u_pop]
│
└─ down_pops: [
       [Individual_1, Individual_2, ..., Individual_d_pop],  # Sub-population 1
       [Individual_1, Individual_2, ..., Individual_d_pop],  # Sub-population 2
       ...
       [Individual_1, Individual_2, ..., Individual_d_pop]   # Sub-population d_num
   ]
"""