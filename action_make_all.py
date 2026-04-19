import copy
import scad

def main(**kwargs):
    
    make_scad = True

    #render scad pieces
    if make_scad:
        kwargs2 = copy.deepcopy(kwargs)
        kwargs2["typ"] = "all"
        scad.main(**kwargs2)




if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)